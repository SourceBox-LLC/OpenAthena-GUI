# OpenAthena UI

A beautiful, intuitive web interface for OpenAthena, similar to AWS Athena. This Flask-based UI provides a user-friendly way to interact with OpenAthena's SQL query capabilities.

## Features

- **Interactive SQL Editor** with syntax highlighting and formatting
- **Query Results Display** with downloadable results in CSV and JSON formats
- **Table Browser** showing schema information and sample data
- **Health Monitoring Dashboard** to check system status
- **Responsive Design** that works on desktop and tablets
- **Dark Mode Support** for comfortable late-night querying

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenAthena server running locally or remotely

### Setup

1. Install the required packages:

```bash
cd openathena-ui
pip install flask requests
```

2. Run the application:

```bash
python app.py
```

3. Open your browser and navigate to http://localhost:5000

## Usage

### Connecting to OpenAthena

By default, the UI connects to an OpenAthena instance running at http://localhost:8000. To change this:

1. Navigate to the Settings page
2. Enter your OpenAthena server URL
3. Click "Save Settings"
4. Test the connection to verify it works

### Running Queries

1. Go to the Query Editor page
2. Write your SQL query in the editor
3. Click "Run Query" to execute
4. View results in the table below
5. Download results as CSV or JSON if needed

### Exploring Tables

1. Navigate to the Tables page to see all available tables
2. Click on a table to see its schema and sample data
3. Use the "Query Table" button to quickly run a SELECT query

### Monitoring Health

The Health page provides a comprehensive view of your OpenAthena instance's status:

- API connectivity
- Table availability
- Query execution capability
- Advanced diagnostics

## Development

### Project Structure

```
openathena-ui/
├── app.py                 # Main Flask application
├── static/
│   ├── css/               # Stylesheets
│   │   └── style.css      # Main CSS file
│   └── js/                # JavaScript files
│       └── main.js        # Main JS functionality
└── templates/             # HTML templates
    ├── base.html          # Base template with layout
    ├── index.html         # Dashboard
    ├── query.html         # Query editor
    ├── tables.html        # Tables browser
    ├── health.html        # Health monitoring
    └── settings.html      # Settings page
```

## License

Same as OpenAthena - See the main project README for license details.

## Acknowledgements

- Built to work seamlessly with [OpenAthena](https://github.com/SourceBox-LLC/OpenAthena)
- Inspired by AWS Athena's intuitive interface
- Uses Bootstrap for responsive design
- CodeMirror for SQL editing
