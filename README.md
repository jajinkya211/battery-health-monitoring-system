# Battery Health Monitoring & Diagnostic System

A comprehensive full-stack Python application for real-time battery pack health monitoring, diagnostics, and predictive analytics in electric vehicles and energy storage systems.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

This system processes time-series battery telemetry data (voltage, current, temperature) from Battery Management Systems (BMS), applies signal processing algorithms to calculate critical health metrics (State of Charge, State of Health, internal resistance), and provides interactive visualizations for engineering teams to identify degradation patterns and predict battery lifespan.

### Key Features

- **Real-Time Data Processing**: Automated calculation of SoC, SoH, and internal resistance using voltage-current analysis
- **Robust Data Management**: PostgreSQL-backed relational database with full CRUD operations
- **Interactive Dashboards**: Plotly/Dash visualizations with health threshold indicators
- **Automated Health Alerts**: Configurable warning/critical thresholds for proactive maintenance
- **Team Collaboration**: Diagnostic notes system for cross-functional engineering teams
- **RESTful API**: Full API documentation with OpenAPI/Swagger support
- **Production-Ready**: Comprehensive test suite, error handling, and Docker support

---

## Architecture

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI | High-performance async REST API |
| **Database** | PostgreSQL 15 | Relational data storage with ACID compliance |
| **ORM** | SQLAlchemy | Database abstraction and migrations |
| **Processing** | NumPy, SciPy, Pandas | Signal processing and health calculations |
| **Frontend** | Plotly Dash | Interactive data visualization |
| **Testing** | Pytest | Unit and integration tests |
| **Deployment** | Docker Compose | Containerized orchestration |

### System Architecture
```
┌─────────────────┐
│  BMS Data CSV   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   FastAPI Backend (Port 8000)       │
│  ┌──────────────────────────────┐   │
│  │  Upload Handler              │   │
│  └──────────┬───────────────────┘   │
│             ▼                        │
│  ┌──────────────────────────────┐   │
│  │  Health Processing Engine    │   │
│  │  • SoC Calculation           │   │
│  │  • SoH Estimation            │   │
│  │  • Resistance Analysis       │   │
│  └──────────┬───────────────────┘   │
│             ▼                        │
│  ┌──────────────────────────────┐   │
│  │  PostgreSQL Database         │   │
│  │  • Battery Packs             │   │
│  │  • Measurements              │   │
│  │  • Health Metrics            │   │
│  │  • Diagnostic Notes          │   │
│  └──────────┬───────────────────┘   │
└─────────────┼───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Dash Dashboard (Port 8050)        │
│  • Health Metrics Visualization     │
│  • Threshold Comparison             │
│  • Team Collaboration Tools         │
└─────────────────────────────────────┘
```

---

## Database Schema
```sql
battery_packs (pack_id, model, chemistry, capacity_ah, ...)
    │
    ├──< cells (cell_id, pack_id, position, nominal_voltage)
    │      │
    │      └──< health_metrics (metric_id, cell_id, soc_percent, 
    │                           soh_percent, internal_resistance, ...)
    │             │
    │             └──< diagnostic_notes (note_id, metric_id, user_name, note)
    │
    └──< measurements (measurement_id, pack_id, timestamp, condition, ...)

health_thresholds (threshold_id, metric_type, min_value, max_value, severity)
users (user_id, name, email, role)
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15
- pip/virtualenv

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/jajinkya211/battery-health-monitor.git
cd battery-health-monitor
```

2. **Set up virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**
```bash
# Create database and user
createdb battery_health_db
psql -U postgres -d battery_health_db -f migrations/init_schema.sql
```

5. **Configure environment** (optional)
```bash
export DATABASE_URL="postgresql://batteryuser:batterypass@localhost:5432/battery_health_db"
```

6. **Start the backend**
```bash
uvicorn backend.app:app --reload
```

7. **Start the dashboard** (in a new terminal)
```bash
source venv/bin/activate
python -m frontend.dashboard
```

8. **Access the application**
- Dashboard: http://localhost:8050
- API Documentation: http://localhost:8000/docs
- API Health Check: http://localhost:8000/health

---

## 🐳 Docker Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Usage Guide

### 1. Upload Battery Measurement Data

**Via Dashboard:**
1. Navigate to http://localhost:8050
2. Select battery pack from dropdown
3. Enter test condition (e.g., "charging", "discharging", "idle")
4. Upload CSV file with format:
```csv
timestamp,cell_id,voltage_v,current_a,temperature_c
2024-01-15 08:00:00,1,3.65,2.5,25.3
2024-01-15 08:00:00,2,3.64,2.5,25.5
```
5. Click "Upload and Process"

**Via API:**
```bash
curl -X POST "http://localhost:8000/measurements" \
  -F "pack_id=1" \
  -F "condition=charging" \
  -F "file=@data/sample_battery_data.csv"
```

### 2. View Health Metrics

1. Click "Refresh Measurements"
2. Select a measurement from dropdown
3. View interactive charts:
   - State of Health (SoH) by cell
   - State of Charge (SoC) trends
   - Internal resistance analysis
   - Temperature distribution

### 3. Add Diagnostic Notes

1. Identify metric_id from the summary table
2. Enter your name and observations
3. Submit note for team collaboration

---

## Health Calculation Methodology

### State of Charge (SoC)
- **Method**: Open Circuit Voltage (OCV) lookup table with linear interpolation
- **Input**: Cell voltage (V)
- **Output**: SoC percentage (0-100%)

### State of Health (SoH)
- **Method**: Multi-factor estimation combining:
  - Capacity fade analysis
  - Internal resistance growth
  - Cycle count degradation
- **Output**: SoH percentage (0-100%)

### Internal Resistance
- **Method**: Linear regression on voltage-current relationship during load
- **Formula**: R = -ΔV/ΔI
- **Output**: Resistance in milliohms (mΩ)

---

## Testing

Run the test suite:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

---

## API Endpoints

### Battery Packs
- `POST /battery_packs` - Create new battery pack
- `GET /battery_packs` - List all battery packs
- `GET /battery_packs/{pack_id}` - Get specific pack

### Measurements
- `POST /measurements` - Upload measurement file
- `GET /measurements?pack_id={id}` - Get measurements

### Health Metrics
- `GET /health_metrics?measurement_id={id}` - Get metrics
- `GET /health_metrics?passes_threshold=false` - Get failing metrics

### Diagnostic Notes
- `POST /diagnostic_notes` - Create note
- `GET /diagnostic_notes?metric_id={id}` - Get notes

**Full API documentation**: http://localhost:8000/docs

---

## Project Structure
```
battery-health-monitor/
├── backend/                    # FastAPI backend application
│   ├── app.py                 # Main API routes and endpoints
│   ├── models.py              # SQLAlchemy ORM models
│   ├── database.py            # Database configuration
│   ├── health_processing.py   # SoC/SoH calculation algorithms
│   ├── upload_handler.py      # File upload and processing
│   └── diagnostics.py         # Diagnostic notes management
├── frontend/                   # Plotly Dash dashboard
│   ├── dashboard.py           # Main dashboard application
│   ├── charts.py              # Chart generation logic
│   └── forms.py               # Form components
├── config/                     # Configuration files
│   └── settings.py            # Application settings
├── data/                       # Data storage
│   └── sample_battery_data.csv
├── tests/                      # Test suite
│   ├── test_api.py
│   ├── test_processing.py
│   └── test_database.py
├── migrations/                 # Database migrations
│   └── init_schema.sql
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Container definition
└── README.md                   # This file
```

---


## Future Enhancements

- [ ] Machine learning-based degradation prediction
- [ ] Real-time streaming data support (MQTT/WebSocket)
- [ ] Multi-pack comparison analytics
- [ ] Automated anomaly detection with alerting
- [ ] Export to standardized formats (HDF5, Parquet)
- [ ] Mobile app for field diagnostics
- [ ] Integration with fleet management systems

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Ajinkya Jadhav**
- GitHub: [@jajinkya211](https://github.com/jajinkya211)
- LinkedIn: [Ajinkya](https://linkedin.com/in/jajinkya211)

---

## Acknowledgments

- Battery health calculation algorithms based on industry best practices
- Sample data generated for demonstration purposes
- Built with modern Python web frameworks and data science libraries


**If you find this project useful, please consider giving it a star!**
