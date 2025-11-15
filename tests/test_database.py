"""Database model tests"""
import pytest
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, BatteryPack, Cell, Measurement

TEST_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def test_battery_pack_creation():
    """Test battery pack model"""
    db = TestingSessionLocal()
    
    pack = BatteryPack(
        model="Test Pack",
        chemistry="NMC",
        capacity_ah=50.0,
        manufacture_date=date(2024, 1, 1)
    )
    
    db.add(pack)
    db.commit()
    db.refresh(pack)
    
    assert pack.pack_id is not None
    assert pack.model == "Test Pack"
    
    db.close()


def test_cell_creation():
    """Test cell model"""
    db = TestingSessionLocal()
    
    pack = BatteryPack(
        model="Test Pack",
        chemistry="NMC",
        capacity_ah=50.0,
        manufacture_date=date(2024, 1, 1)
    )
    db.add(pack)
    db.commit()
    
    cell = Cell(
        pack_id=pack.pack_id,
        position="1A",
        nominal_voltage=3.7
    )
    db.add(cell)
    db.commit()
    db.refresh(cell)
    
    assert cell.cell_id is not None
    assert cell.pack_id == pack.pack_id
    
    db.close()


def test_relationships():
    """Test model relationships"""
    db = TestingSessionLocal()
    
    pack = BatteryPack(
        model="Test Pack",
        chemistry="NMC",
        capacity_ah=50.0,
        manufacture_date=date(2024, 1, 1)
    )
    db.add(pack)
    db.commit()
    
    cell = Cell(
        pack_id=pack.pack_id,
        position="1A",
        nominal_voltage=3.7
    )
    db.add(cell)
    db.commit()
    
    # Test relationship
    retrieved_pack = db.query(BatteryPack).filter(BatteryPack.pack_id == pack.pack_id).first()
    assert len(retrieved_pack.cells) == 1
    assert retrieved_pack.cells[0].position == "1A"
    
    db.close()