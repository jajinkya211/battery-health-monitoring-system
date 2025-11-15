# Detailed Setup Guide

## System Requirements

- **OS**: macOS 10.15+, Ubuntu 20.04+, or Windows 10+
- **Python**: 3.11 or higher
- **PostgreSQL**: 15.x
- **RAM**: Minimum 4GB
- **Disk**: 2GB free space

## Step-by-Step Installation

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Create Database
```bash
createdb battery_health_db
createuser batteryuser -P  # Enter password: batterypass
psql -d battery_health_db -f migrations/init_schema.sql
```

### 3. Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
# Check database connection
psql -U batteryuser -d battery_health_db -c "SELECT * FROM battery_packs;"

# Run tests
pytest tests/ -v
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `pg_isready`
- Check connection string in `config/settings.py`

### Port Conflicts
- Backend: Change `API_PORT` in `config/settings.py`
- Dashboard: Change `DASHBOARD_PORT` in `config/settings.py`

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
```

---

### Create `LICENSE` file:
```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.