"""SQLAlchemy ORM Models for Battery Health Monitoring System"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class BatteryPack(Base):
    __tablename__ = 'battery_packs'
    
    pack_id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String(100), nullable=False)
    chemistry = Column(String(50), nullable=False)
    capacity_ah = Column(Float, nullable=False)
    manufacture_date = Column(Date, nullable=False)
    notes = Column(Text)
    
    cells = relationship("Cell", back_populates="pack", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="pack", cascade="all, delete-orphan")


class Cell(Base):
    __tablename__ = 'cells'
    
    cell_id = Column(Integer, primary_key=True, autoincrement=True)
    pack_id = Column(Integer, ForeignKey('battery_packs.pack_id'), nullable=False)
    position = Column(String(50), nullable=False)
    nominal_voltage = Column(Float, nullable=False)
    
    pack = relationship("BatteryPack", back_populates="cells")
    health_metrics = relationship("HealthMetric", back_populates="cell", cascade="all, delete-orphan")


class Measurement(Base):
    __tablename__ = 'measurements'
    
    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    pack_id = Column(Integer, ForeignKey('battery_packs.pack_id'), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    condition = Column(String(100), nullable=False)
    raw_data_path = Column(String(500), nullable=False)
    
    pack = relationship("BatteryPack", back_populates="measurements")
    health_metrics = relationship("HealthMetric", back_populates="measurement", cascade="all, delete-orphan")


class HealthMetric(Base):
    __tablename__ = 'health_metrics'
    
    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_id = Column(Integer, ForeignKey('measurements.measurement_id'), nullable=False)
    cell_id = Column(Integer, ForeignKey('cells.cell_id'), nullable=False)
    soc_percent = Column(Float, nullable=False)
    soh_percent = Column(Float, nullable=False)
    internal_resistance = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    passes_threshold = Column(Boolean, nullable=False, default=True)
    
    measurement = relationship("Measurement", back_populates="health_metrics")
    cell = relationship("Cell", back_populates="health_metrics")
    diagnostic_notes = relationship("DiagnosticNote", back_populates="metric", cascade="all, delete-orphan")


class HealthThreshold(Base):
    __tablename__ = 'health_thresholds'
    
    threshold_id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String(50), nullable=False)
    min_value = Column(Float)
    max_value = Column(Float)
    severity = Column(String(50), nullable=False)


class DiagnosticNote(Base):
    __tablename__ = 'diagnostic_notes'
    
    note_id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, ForeignKey('health_metrics.metric_id'), nullable=False)
    user_name = Column(String(100), nullable=False)
    note = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    metric = relationship("HealthMetric", back_populates="diagnostic_notes")


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(50), nullable=False)