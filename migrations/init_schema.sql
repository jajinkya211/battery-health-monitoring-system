-- Battery Health Monitoring System - Database Schema
-- PostgreSQL

CREATE TABLE IF NOT EXISTS battery_packs (
    pack_id SERIAL PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    chemistry VARCHAR(50) NOT NULL,
    capacity_ah FLOAT NOT NULL,
    manufacture_date DATE NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS cells (
    cell_id SERIAL PRIMARY KEY,
    pack_id INTEGER NOT NULL REFERENCES battery_packs(pack_id) ON DELETE CASCADE,
    position VARCHAR(50) NOT NULL,
    nominal_voltage FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id SERIAL PRIMARY KEY,
    pack_id INTEGER NOT NULL REFERENCES battery_packs(pack_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    condition VARCHAR(100) NOT NULL,
    raw_data_path VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS health_metrics (
    metric_id SERIAL PRIMARY KEY,
    measurement_id INTEGER NOT NULL REFERENCES measurements(measurement_id) ON DELETE CASCADE,
    cell_id INTEGER NOT NULL REFERENCES cells(cell_id) ON DELETE CASCADE,
    soc_percent FLOAT NOT NULL,
    soh_percent FLOAT NOT NULL,
    internal_resistance FLOAT NOT NULL,
    temperature_c FLOAT NOT NULL,
    passes_threshold BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS health_thresholds (
    threshold_id SERIAL PRIMARY KEY,
    metric_type VARCHAR(50) NOT NULL,
    min_value FLOAT,
    max_value FLOAT,
    severity VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS diagnostic_notes (
    note_id SERIAL PRIMARY KEY,
    metric_id INTEGER NOT NULL REFERENCES health_metrics(metric_id) ON DELETE CASCADE,
    user_name VARCHAR(100) NOT NULL,
    note TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL
);

-- Create indexes for common queries
CREATE INDEX idx_cells_pack_id ON cells(pack_id);
CREATE INDEX idx_measurements_pack_id ON measurements(pack_id);
CREATE INDEX idx_health_metrics_measurement_id ON health_metrics(measurement_id);
CREATE INDEX idx_health_metrics_cell_id ON health_metrics(cell_id);
CREATE INDEX idx_diagnostic_notes_metric_id ON diagnostic_notes(metric_id);

-- Insert sample data
INSERT INTO battery_packs (model, chemistry, capacity_ah, manufacture_date, notes) VALUES
('EV Battery Pack A', 'NMC', 50.0, '2023-06-15', 'Fleet vehicle battery'),
('Energy Storage B', 'LFP', 100.0, '2023-08-20', 'Stationary storage');

INSERT INTO cells (pack_id, position, nominal_voltage) VALUES
(1, '1A', 3.7),
(1, '1B', 3.7),
(1, '2A', 3.7),
(1, '2B', 3.7);

INSERT INTO health_thresholds (metric_type, min_value, max_value, severity) VALUES
('soh', 80.0, NULL, 'warning'),
('soh', 70.0, NULL, 'critical'),
('resistance', NULL, 100.0, 'warning'),
('resistance', NULL, 150.0, 'critical'),
('temperature', NULL, 45.0, 'warning'),
('temperature', NULL, 55.0, 'critical');

INSERT INTO users (name, email, role) VALUES
('Alice Engineer', 'alice@example.com', 'engineer'),
('Bob Analyst', 'bob@example.com', 'analyst'),
('Charlie Admin', 'charlie@example.com', 'admin');
