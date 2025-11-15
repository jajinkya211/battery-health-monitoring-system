"""FastAPI application with all REST endpoints"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel

from backend.database import get_db_session, init_db
from backend.models import (
    BatteryPack, Cell, Measurement, HealthMetric, 
    HealthThreshold, DiagnosticNote, User
)
from backend.upload_handler import UploadHandler
from backend.diagnostics import DiagnosticsManager

# Initialize FastAPI app
app = FastAPI(title="Battery Health Monitoring System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Pydantic models for request/response
class BatteryPackCreate(BaseModel):
    model: str
    chemistry: str
    capacity_ah: float
    manufacture_date: date
    notes: Optional[str] = None

class CellCreate(BaseModel):
    pack_id: int
    position: str
    nominal_voltage: float

class MeasurementCreate(BaseModel):
    pack_id: int
    condition: str

class HealthThresholdCreate(BaseModel):
    metric_type: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    severity: str

class DiagnosticNoteCreate(BaseModel):
    metric_id: int
    user_name: str
    note: str

class UserCreate(BaseModel):
    name: str
    email: str
    role: str


# ===== Battery Pack Endpoints =====
@app.post("/battery_packs", status_code=201)
def create_battery_pack(pack: BatteryPackCreate, db: Session = Depends(get_db_session)):
    """Create a new battery pack"""
    db_pack = BatteryPack(**pack.dict())
    db.add(db_pack)
    db.commit()
    db.refresh(db_pack)
    return db_pack


@app.get("/battery_packs")
def get_battery_packs(db: Session = Depends(get_db_session)):
    """Get all battery packs"""
    return db.query(BatteryPack).all()


@app.get("/battery_packs/{pack_id}")
def get_battery_pack(pack_id: int, db: Session = Depends(get_db_session)):
    """Get specific battery pack"""
    pack = db.query(BatteryPack).filter(BatteryPack.pack_id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Battery pack not found")
    return pack


# ===== Cell Endpoints =====
@app.post("/cells", status_code=201)
def create_cell(cell: CellCreate, db: Session = Depends(get_db_session)):
    """Create a new cell"""
    db_cell = Cell(**cell.dict())
    db.add(db_cell)
    db.commit()
    db.refresh(db_cell)
    return db_cell


@app.get("/cells")
def get_cells(pack_id: Optional[int] = None, db: Session = Depends(get_db_session)):
    """Get cells, optionally filtered by pack_id"""
    query = db.query(Cell)
    if pack_id:
        query = query.filter(Cell.pack_id == pack_id)
    return query.all()


# ===== Measurement Endpoints =====
@app.post("/measurements", status_code=201)
async def create_measurement(
    pack_id: int = Form(...),
    condition: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session)
):
    """Upload measurement file and process health metrics"""
    # Create measurement record
    measurement = Measurement(
        pack_id=pack_id,
        timestamp=datetime.utcnow(),
        condition=condition,
        raw_data_path=""  # Will be updated after file save
    )
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    
    # Save file and update path
    handler = UploadHandler()
    filepath = await handler.save_upload(file, measurement.measurement_id)
    measurement.raw_data_path = filepath
    db.commit()
    
    # Process and store metrics
    try:
        metrics = handler.process_and_store_metrics(filepath, measurement.measurement_id)
        return {
            "measurement": measurement,
            "metrics_created": len(metrics)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/measurements")
def get_measurements(pack_id: Optional[int] = None, db: Session = Depends(get_db_session)):
    """Get measurements, optionally filtered by pack_id"""
    query = db.query(Measurement)
    if pack_id:
        query = query.filter(Measurement.pack_id == pack_id)
    return query.order_by(Measurement.timestamp.desc()).all()


# ===== Health Metrics Endpoints =====
@app.get("/health_metrics")
def get_health_metrics(
    measurement_id: Optional[int] = None,
    passes_threshold: Optional[bool] = None,
    db: Session = Depends(get_db_session)
):
    """Get health metrics with optional filters"""
    query = db.query(HealthMetric)
    if measurement_id:
        query = query.filter(HealthMetric.measurement_id == measurement_id)
    if passes_threshold is not None:
        query = query.filter(HealthMetric.passes_threshold == passes_threshold)
    return query.all()


@app.get("/health_metrics/{metric_id}")
def get_health_metric(metric_id: int, db: Session = Depends(get_db_session)):
    """Get specific health metric"""
    metric = db.query(HealthMetric).filter(HealthMetric.metric_id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Health metric not found")
    return metric


# ===== Health Threshold Endpoints =====
@app.post("/health_thresholds", status_code=201)
def create_health_threshold(threshold: HealthThresholdCreate, db: Session = Depends(get_db_session)):
    """Create a new health threshold"""
    db_threshold = HealthThreshold(**threshold.dict())
    db.add(db_threshold)
    db.commit()
    db.refresh(db_threshold)
    return db_threshold


@app.get("/health_thresholds")
def get_health_thresholds(db: Session = Depends(get_db_session)):
    """Get all health thresholds"""
    return db.query(HealthThreshold).all()


# ===== Diagnostic Notes Endpoints =====
@app.post("/diagnostic_notes", status_code=201)
def create_diagnostic_note(note: DiagnosticNoteCreate, db: Session = Depends(get_db_session)):
    """Create a new diagnostic note"""
    return DiagnosticsManager.create_note(db, note.metric_id, note.user_name, note.note)


@app.get("/diagnostic_notes")
def get_diagnostic_notes(
    metric_id: Optional[int] = None,
    user_name: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """Get diagnostic notes with optional filters"""
    if metric_id:
        return DiagnosticsManager.get_notes_by_metric(db, metric_id)
    elif user_name:
        return DiagnosticsManager.get_notes_by_user(db, user_name)
    else:
        return db.query(DiagnosticNote).order_by(DiagnosticNote.timestamp.desc()).all()


@app.delete("/diagnostic_notes/{note_id}")
def delete_diagnostic_note(note_id: int, db: Session = Depends(get_db_session)):
    """Delete a diagnostic note"""
    success = DiagnosticsManager.delete_note(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Diagnostic note not found")
    return {"message": "Diagnostic note deleted successfully"}


# ===== User Endpoints =====
@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db_session)):
    """Create a new user"""
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users")
def get_users(db: Session = Depends(get_db_session)):
    """Get all users"""
    return db.query(User).all()


# Health check endpoint
@app.get("/health")
def health_check():
    """API health check"""
    return {"status": "healthy", "service": "Battery Health Monitoring System"}