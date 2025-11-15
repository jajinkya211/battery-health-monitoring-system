"""File upload handling and processing orchestration"""
import os
import shutil
from datetime import datetime
from typing import Dict, List
from fastapi import UploadFile
from backend.health_processing import BatteryHealthProcessor
from backend.models import HealthMetric, HealthThreshold
from backend.database import get_db
from config.settings import DATA_DIR


class UploadHandler:
    """Handle file uploads and trigger health metric processing"""
    
    def __init__(self):
        self.processor = BatteryHealthProcessor()
        os.makedirs(DATA_DIR, exist_ok=True)
    
    async def save_upload(self, file: UploadFile, measurement_id: int) -> str:
        """
        Save uploaded file to data directory
        
        Args:
            file: Uploaded file
            measurement_id: Associated measurement ID
            
        Returns:
            Path to saved file
        """
        filename = f"measurement_{measurement_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return filepath
    
    def process_and_store_metrics(self, 
                                  filepath: str, 
                                  measurement_id: int) -> List[HealthMetric]:
        """
        Process measurement file and store health metrics in database
        
        Args:
            filepath: Path to measurement CSV file
            measurement_id: Associated measurement ID
            
        Returns:
            List of created HealthMetric objects
        """
        # Process file
        metrics_data = self.processor.process_measurement_file(filepath)
        
        # Get thresholds from database
        with get_db() as db:
            thresholds = db.query(HealthThreshold).all()
            threshold_dict = {t.metric_type: (t.min_value, t.max_value) 
                            for t in thresholds}
        
        # Create metric objects
        health_metrics = []
        for metric_data in metrics_data:
            # Check thresholds
            passes = self._check_thresholds(metric_data, threshold_dict)
            
            metric = HealthMetric(
                measurement_id=measurement_id,
                cell_id=metric_data['cell_id'],
                soc_percent=metric_data['soc_percent'],
                soh_percent=metric_data['soh_percent'],
                internal_resistance=metric_data['internal_resistance'],
                temperature_c=metric_data['temperature_c'],
                passes_threshold=passes
            )
            health_metrics.append(metric)
        
        # Store in database
        with get_db() as db:
            db.add_all(health_metrics)
            db.commit()
            for metric in health_metrics:
                db.refresh(metric)
        
        return health_metrics
    
    def _check_thresholds(self, 
                         metric_data: Dict, 
                         thresholds: Dict) -> bool:
        """Check if metrics pass all thresholds"""
        checks = []
        
        # Check SoH
        if 'soh' in thresholds:
            min_val, max_val = thresholds['soh']
            if min_val is not None:
                checks.append(metric_data['soh_percent'] >= min_val)
        
        # Check internal resistance
        if 'resistance' in thresholds:
            min_val, max_val = thresholds['resistance']
            if max_val is not None:
                checks.append(metric_data['internal_resistance'] <= max_val)
        
        # Check temperature
        if 'temperature' in thresholds:
            min_val, max_val = thresholds['temperature']
            if max_val is not None:
                checks.append(metric_data['temperature_c'] <= max_val)
        
        return all(checks) if checks else True