"""Diagnostic notes CRUD operations"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models import DiagnosticNote
from datetime import datetime


class DiagnosticsManager:
    """Manage diagnostic notes for health metrics"""
    
    @staticmethod
    def create_note(db: Session, 
                   metric_id: int, 
                   user_name: str, 
                   note: str) -> DiagnosticNote:
        """Create a new diagnostic note"""
        diagnostic_note = DiagnosticNote(
            metric_id=metric_id,
            user_name=user_name,
            note=note,
            timestamp=datetime.utcnow()
        )
        db.add(diagnostic_note)
        db.commit()
        db.refresh(diagnostic_note)
        return diagnostic_note
    
    @staticmethod
    def get_notes_by_metric(db: Session, metric_id: int) -> List[DiagnosticNote]:
        """Get all notes for a specific metric"""
        return db.query(DiagnosticNote).filter(
            DiagnosticNote.metric_id == metric_id
        ).order_by(DiagnosticNote.timestamp.desc()).all()
    
    @staticmethod
    def get_notes_by_user(db: Session, user_name: str) -> List[DiagnosticNote]:
        """Get all notes by a specific user"""
        return db.query(DiagnosticNote).filter(
            DiagnosticNote.user_name == user_name
        ).order_by(DiagnosticNote.timestamp.desc()).all()
    
    @staticmethod
    def delete_note(db: Session, note_id: int) -> bool:
        """Delete a diagnostic note"""
        note = db.query(DiagnosticNote).filter(
            DiagnosticNote.note_id == note_id
        ).first()
        if note:
            db.delete(note)
            db.commit()
            return True
        return False