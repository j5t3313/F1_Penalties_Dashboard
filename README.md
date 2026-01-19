# F1 Penalty Data Dashboard

A web-based dashboard for analyzing Formula 1 penalty data from 2020-2025. Built with Python Dash and designed for mobile-responsive viewing.

## Overview

This application provides interactive analysis of F1 penalty data across multiple dimensions including drivers, teams, races, and stewards. Data spans the 2020-2025 seasons and includes comprehensive standardization of driver names, team names, allegations, and outcomes.

## Features

- **Overview Dashboard**: Summary statistics and visualizations of penalty trends
- **Driver Analysis**: Individual driver penalty records and patterns
- **Team Analysis**: Team-level penalty aggregations and comparisons
- **Race Breakdown**: Circuit-specific penalty analysis
- **Steward Analysis**: Examination of steward decision patterns
- **Comparison Tools**: Side-by-side comparison capabilities
- **Raw Data View**: Filterable table of all penalty records
- **Mobile-Responsive Design**: Optimized for viewing on mobile devices

## Technical Stack

- **Framework**: Dash 2.14.2
- **UI Components**: Dash Bootstrap Components 1.5.0
- **Data Processing**: Pandas 2.1.4
- **Visualization**: Plotly 5.18.0
- **Excel Parsing**: openpyxl 3.1.2
- **Web Server**: Gunicorn 21.2.0

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR-USERNAME/f1-penalty-dashboard.git
cd f1-penalty-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure the Excel data file is present:
```
F1 Penalty Data Dashboard Working.xlsx
```

## Usage

### Local Development

Run the application locally:
```bash
python app.py
```

Access the dashboard at `http://localhost:8050`

### Production Deployment

The application is configured for Railway deployment using Gunicorn:
```bash
gunicorn app:server
```

## Data Structure

### Source Data

Data is sourced from an Excel workbook with sheets for each season (2020-2025). Each sheet contains the following fields:

- Grand Prix
- Date
- Driver
- Team
- Time
- Session
- Lap
- Allegation
- Outcome
- Grid Penalty (numeric)
- Time Penalty (seconds)
- Penalty Points

### Data Standardization

The application performs extensive data cleaning:

- **Driver Names**: 52 variations standardized to canonical forms (e.g., "Alexander Albon" and "Alex Albon" → "Alexander Albon")
- **Team Names**: Multiple variations consolidated (e.g., "Red Bull", "Red Bull Racing" → "Red Bull Racing")
- **Allegations**: 75 distinct values mapped to 37 canonical categories
- **Outcomes**: 22 distinct values mapped to 13 standardized outcomes
- **Special Handling**: Grid penalties parsed from text outcomes; pit lane starts coded appropriately
- **Invalid Records**: Non-driver entries filtered out

### Color Coding

Teams are assigned official F1 team colors. Driver records use color variations based on team affiliation at the time of the penalty.

## Project Structure
```
.
├── app.py                                    # Main application file
├── requirements.txt                          # Python dependencies
├── Procfile                                  # Railway deployment configuration
├── runtime.txt                               # Python version specification
├── F1 Penalty Data Dashboard Working.xlsx   # Source data
└── README.md                                 # Documentation
```

## Filtering Capabilities

The dashboard supports case-insensitive filtering across:
- Seasons
- Grand Prix
- Drivers
- Teams
- Sessions
- Allegations
- Outcomes
- Stewards

Filters are applied using an offcanvas panel optimized for mobile viewing.

## Deployment

The application is deployed on Railway with automatic deployments triggered by GitHub pushes to the main branch.

### Environment Configuration

- **PORT**: Automatically set by Railway
- **HOST**: 0.0.0.0 for external access
- **DEBUG**: False in production

## License

[Specify your license here]

## Author

Jessica - BI/Data Analyst specializing in healthcare analytics and Formula 1 data science

## Acknowledgments

Data compiled from official FIA penalty decisions for the 2020-2025 Formula 1 seasons.
