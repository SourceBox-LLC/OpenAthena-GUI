"""
OpenAthena Web UI

A Flask-based UI for interacting with OpenAthena, inspired by AWS Athena.
"""

import os
import json
import time
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash

# For template context
from jinja2 import Environment

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "openathena-development-key")

# Add template context processors
@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    return {"now": now}

# Configuration
DEFAULT_OPENATHENA_URL = "http://localhost:8000"


@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/query', methods=['GET', 'POST'])
def query():
    """Query editor and results page."""
    if request.method == 'POST':
        sql_query = request.form.get('query', '')
        openathena_url = session.get('openathena_url', DEFAULT_OPENATHENA_URL)
        
        try:
            # Execute query
            start_time = time.time()
            response = requests.post(
                f"{openathena_url}/sql",
                data=sql_query,
                headers={"Content-Type": "text/plain", "Accept": "application/json"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                # Try to get JSON response for display
                try:
                    result = response.json()
                    execution_time = int((end_time - start_time) * 1000)
                    return render_template(
                        'query.html', 
                        query=sql_query, 
                        result=result,
                        execution_time=execution_time,
                        success=True
                    )
                except:
                    # Handle non-JSON responses (like Arrow)
                    return render_template(
                        'query.html', 
                        query=sql_query, 
                        error="Received non-JSON response. Use the API directly for this query type.",
                        success=False
                    )
            else:
                error_message = f"Error: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_message = f"{error_message} - {error_detail.get('detail', '')}"
                except:
                    pass
                
                return render_template('query.html', query=sql_query, error=error_message, success=False)
                
        except Exception as e:
            return render_template('query.html', query=sql_query, error=str(e), success=False)
    
    # GET request - just show the query interface
    return render_template('query.html')


@app.route('/tables')
def tables():
    """Show available tables."""
    openathena_url = session.get('openathena_url', DEFAULT_OPENATHENA_URL)
    
    try:
        response = requests.get(f"{openathena_url}/tables")
        if response.status_code == 200:
            tables_data = response.json()
            return render_template('tables.html', tables=tables_data.get('tables', {}))
        else:
            flash(f"Error retrieving tables: {response.status_code}", "error")
            return render_template('tables.html', tables={})
    except Exception as e:
        flash(f"Connection error: {str(e)}", "error")
        return render_template('tables.html', tables={})


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Settings page for OpenAthena connection."""
    if request.method == 'POST':
        openathena_url = request.form.get('openathena_url', DEFAULT_OPENATHENA_URL)
        session['openathena_url'] = openathena_url
        
        # Test connection
        try:
            response = requests.get(f"{openathena_url}/health")
            if response.status_code == 200:
                flash("Successfully connected to OpenAthena", "success")
            else:
                flash(f"Connection test failed: {response.status_code}", "error")
        except Exception as e:
            flash(f"Connection error: {str(e)}", "error")
        
        return redirect(url_for('settings'))
    
    # GET request
    return render_template(
        'settings.html', 
        openathena_url=session.get('openathena_url', DEFAULT_OPENATHENA_URL)
    )


@app.route('/health')
def health():
    """Health check and system status page."""
    openathena_url = session.get('openathena_url', DEFAULT_OPENATHENA_URL)
    
    status = {
        "api": {"status": "unknown", "message": "Not checked"},
        "tables": {"status": "unknown", "message": "Not checked"},
        "query": {"status": "unknown", "message": "Not checked"}
    }
    
    # Check API health
    try:
        response = requests.get(f"{openathena_url}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                status["api"] = {"status": "healthy", "message": "API is responding"}
            else:
                status["api"] = {"status": "degraded", "message": f"Status: {data.get('status')}"}
        else:
            status["api"] = {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        status["api"] = {"status": "unhealthy", "message": str(e)}
    
    # Check tables
    try:
        response = requests.get(f"{openathena_url}/tables", timeout=2)
        if response.status_code == 200:
            data = response.json()
            table_count = len(data.get("tables", {}))
            if table_count > 0:
                status["tables"] = {"status": "healthy", "message": f"Found {table_count} tables"}
            else:
                status["tables"] = {"status": "degraded", "message": "No tables available"}
        else:
            status["tables"] = {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        status["tables"] = {"status": "unhealthy", "message": str(e)}
    
    # Check query capability
    try:
        response = requests.post(
            f"{openathena_url}/sql",
            data="SELECT 1 as test",
            headers={"Content-Type": "text/plain"},
            timeout=3
        )
        if response.status_code == 200:
            status["query"] = {"status": "healthy", "message": "Query execution working"}
        else:
            status["query"] = {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        status["query"] = {"status": "unhealthy", "message": str(e)}
    
    # Determine overall status
    overall = "healthy"
    if any(s["status"] == "unhealthy" for s in status.values()):
        overall = "unhealthy"
    elif any(s["status"] == "degraded" for s in status.values()):
        overall = "degraded"
    
    return render_template('health.html', status=status, overall=overall)


@app.route('/api/execute-query', methods=['POST'])
def api_execute_query():
    """API endpoint for executing queries asynchronously."""
    sql_query = request.json.get('query', '')
    openathena_url = session.get('openathena_url', DEFAULT_OPENATHENA_URL)
    
    try:
        # Execute query
        start_time = time.time()
        response = requests.post(
            f"{openathena_url}/sql",
            data=sql_query,
            headers={"Content-Type": "text/plain", "Accept": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            # Try to parse JSON response
            try:
                result = response.json()
                execution_time = int((end_time - start_time) * 1000)
                return jsonify({
                    "success": True,
                    "data": result,
                    "execution_time": execution_time
                })
            except:
                return jsonify({
                    "success": False,
                    "error": "Received non-JSON response"
                }), 400
        else:
            error_message = f"Error: {response.status_code}"
            try:
                error_detail = response.json()
                error_message = f"{error_message} - {error_detail.get('detail', '')}"
            except:
                pass
            
            return jsonify({
                "success": False,
                "error": error_message
            }), response.status_code
                
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host='0.0.0.0', port=port, debug=debug)
