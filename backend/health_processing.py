"""Battery health metrics calculation module"""
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from typing import Dict, List, Tuple


class BatteryHealthProcessor:
    """Process battery measurement data and calculate health metrics"""
    
    # Voltage-SoC lookup table for NMC chemistry (simplified)
    VOLTAGE_SOC_TABLE = {
        2.75: 0, 3.0: 5, 3.3: 10, 3.5: 20, 3.6: 30,
        3.65: 40, 3.7: 50, 3.75: 60, 3.8: 70, 3.9: 80,
        4.0: 90, 4.1: 95, 4.2: 100
    }
    
    def __init__(self, nominal_capacity_ah: float = 50.0):
        self.nominal_capacity_ah = nominal_capacity_ah
        self._build_soc_interpolator()
    
    def _build_soc_interpolator(self):
        """Build voltage to SoC interpolation function"""
        voltages = sorted(self.VOLTAGE_SOC_TABLE.keys())
        socs = [self.VOLTAGE_SOC_TABLE[v] for v in voltages]
        self.soc_interpolator = interp1d(voltages, socs, 
                                         kind='linear', 
                                         fill_value='extrapolate')
    
    def estimate_soc(self, voltage: float) -> float:
        """
        Estimate State of Charge from voltage
        
        Args:
            voltage: Cell voltage in volts
            
        Returns:
            SoC in percentage (0-100)
        """
        soc = float(self.soc_interpolator(voltage))
        return np.clip(soc, 0, 100)
    
    def calculate_internal_resistance(self, 
                                     voltage_data: np.ndarray, 
                                     current_data: np.ndarray) -> float:
        """
        Calculate internal resistance using voltage-current relationship
        
        Args:
            voltage_data: Array of voltage measurements
            current_data: Array of current measurements
            
        Returns:
            Internal resistance in milliohms
        """
        if len(voltage_data) < 2 or len(current_data) < 2:
            return 0.0
        
        # Remove zero current points
        mask = current_data != 0
        if mask.sum() < 2:
            return 0.0
        
        v_filtered = voltage_data[mask]
        i_filtered = current_data[mask]
        
        # Linear regression: V = V_oc - I*R
        # Resistance is negative slope
        coeffs = np.polyfit(i_filtered, v_filtered, 1)
        resistance_ohms = -coeffs[0]  # Negative slope
        
        # Convert to milliohms
        return max(0, resistance_ohms * 1000)
    
    def estimate_soh(self, 
                    current_capacity_ah: float = None,
                    internal_resistance: float = None,
                    cycles: int = 0) -> float:
        """
        Estimate State of Health based on capacity fade and resistance growth
        
        Args:
            current_capacity_ah: Current measured capacity
            internal_resistance: Internal resistance in milliohms
            cycles: Number of charge cycles
            
        Returns:
            SoH in percentage (0-100)
        """
        soh_factors = []
        
        # Capacity-based SoH
        if current_capacity_ah is not None:
            capacity_soh = (current_capacity_ah / self.nominal_capacity_ah) * 100
            soh_factors.append(capacity_soh)
        
        # Resistance-based SoH (typical new cell: 50mΩ, aged: 150mΩ)
        if internal_resistance is not None:
            base_resistance = 50.0  # mΩ
            aged_resistance = 150.0  # mΩ
            if internal_resistance <= base_resistance:
                resistance_soh = 100.0
            elif internal_resistance >= aged_resistance:
                resistance_soh = 70.0
            else:
                resistance_soh = 100 - 30 * (internal_resistance - base_resistance) / (aged_resistance - base_resistance)
            soh_factors.append(resistance_soh)
        
        # Cycle-based degradation (rough estimate)
        if cycles > 0:
            # Assume 80% health at 2000 cycles (simplified)
            cycle_soh = 100 - (cycles / 2000) * 20
            soh_factors.append(max(70, cycle_soh))
        
        if not soh_factors:
            return 100.0
        
        return np.clip(np.mean(soh_factors), 0, 100)
    
    def process_measurement_file(self, filepath: str) -> List[Dict]:
        """
        Process uploaded measurement CSV and extract health metrics
        
        Args:
            filepath: Path to CSV file with columns: timestamp, cell_id, voltage_v, current_a, temperature_c
            
        Returns:
            List of metric dictionaries
        """
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        metrics = []
        
        # Process each cell separately
        for cell_id in df['cell_id'].unique():
            cell_data = df[df['cell_id'] == cell_id].sort_values('timestamp')
            
            # Get arrays
            voltages = cell_data['voltage_v'].values
            currents = cell_data['current_a'].values
            temperatures = cell_data['temperature_c'].values
            
            # Calculate metrics
            avg_voltage = np.mean(voltages)
            soc = self.estimate_soc(avg_voltage)
            
            internal_resistance = self.calculate_internal_resistance(voltages, currents)
            soh = self.estimate_soh(internal_resistance=internal_resistance)
            
            avg_temp = np.mean(temperatures)
            
            metrics.append({
                'cell_id': int(cell_id),
                'soc_percent': round(soc, 2),
                'soh_percent': round(soh, 2),
                'internal_resistance': round(internal_resistance, 2),
                'temperature_c': round(avg_temp, 2)
            })
        
        return metrics