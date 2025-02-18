import time
from datetime import datetime
import sqlite3
import threading
import json
import logging
from typing import Optional, Dict, Any
try:
    import RPi.GPIO as GPIO
    from hx711 import HX711
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    
class SensorConfig:
    # HX711 pins
    HX_DATA_PIN = 5
    HX_CLOCK_PIN = 6
    
    # Water level sensor pins
    WATER_TRIG_PIN = 23
    WATER_ECHO_PIN = 24
    
    # Calibration values
    WEIGHT_REFERENCE = 100  # Reference weight in grams
    WEIGHT_SCALE = 1.0     # Scale factor
    
    # Thresholds
    MIN_FOOD_WEIGHT = 10.0  # Minimum food weight to consider bowl not empty (g)
    MIN_WATER_LEVEL = 20.0  # Minimum water level percentage
    
    # Sampling
    SAMPLE_INTERVAL = 1.0   # Time between measurements in seconds
    EATING_THRESHOLD = 5.0  # Weight change to detect eating (g)

class HardwareMonitor:
    def __init__(self, db_path: str = 'cat_feeder.db'):
        self.db_path = db_path
        self.running = False
        self.last_weight = 0.0
        self.last_water_level = 100.0
        self.config = SensorConfig()
        self.setup_logging()
        
        if HARDWARE_AVAILABLE:
            self.setup_gpio()
            self.setup_weight_sensor()
        else:
            self.logger.warning("Hardware libraries not available - running in simulation mode")
    
    def setup_logging(self):
        self.logger = logging.getLogger('HardwareMonitor')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('hardware_monitor.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config.WATER_TRIG_PIN, GPIO.OUT)
        GPIO.setup(self.config.WATER_ECHO_PIN, GPIO.IN)
    
    def setup_weight_sensor(self):
        self.weight_sensor = HX711(
            dout_pin=self.config.HX_DATA_PIN,
            pd_sck_pin=self.config.HX_CLOCK_PIN
        )
        self.weight_sensor.reset()
        self.calibrate_weight_sensor()
    
    def calibrate_weight_sensor(self):
        if not HARDWARE_AVAILABLE:
            return
            
        self.logger.info("Starting weight sensor calibration...")
        self.weight_sensor.tare()
        
        # Use known weight for calibration
        input("Place %dg reference weight on scale and press Enter..." % 
              self.config.WEIGHT_REFERENCE)
        readings = []
        for _ in range(10):
            readings.append(self.weight_sensor.get_value())
            time.sleep(0.1)
        
        average_reading = sum(readings) / len(readings)
        self.config.WEIGHT_SCALE = self.config.WEIGHT_REFERENCE / average_reading
        self.logger.info(f"Calibration complete. Scale factor: {self.config.WEIGHT_SCALE}")
    
    def measure_weight(self) -> float:
        if not HARDWARE_AVAILABLE:
            # Simulation mode: return random variations
            import random
            return self.last_weight + random.uniform(-1, 1)
            
        raw_value = self.weight_sensor.get_value()
        weight = raw_value * self.config.WEIGHT_SCALE
        return max(0.0, weight)
    
    def measure_water_level(self) -> float:
        if not HARDWARE_AVAILABLE:
            # Simulation mode: return random variations
            import random
            return max(0.0, min(100.0, self.last_water_level + random.uniform(-2, 2)))
            
        # Send trigger pulse
        GPIO.output(self.config.WATER_TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(self.config.WATER_TRIG_PIN, False)
        
        # Get echo response
        start_time = time.time()
        while GPIO.input(self.config.WATER_ECHO_PIN) == 0:
            if time.time() - start_time > 0.1:
                return self.last_water_level
            
        start_time = time.time()
        while GPIO.input(self.config.WATER_ECHO_PIN) == 1:
            if time.time() - start_time > 0.1:
                return self.last_water_level
                
        duration = time.time() - start_time
        # Convert to percentage (adjust these values based on your container)
        MAX_DISTANCE = 20.0  # cm
        distance = duration * 17150  # Speed of sound / 2
        level = max(0.0, min(100.0, (1 - distance / MAX_DISTANCE) * 100))
        return level
    
    def detect_eating(self, weight_change: float) -> Optional[Dict[str, Any]]:
        if abs(weight_change) >= self.config.EATING_THRESHOLD:
            return {
                'timestamp': datetime.now().isoformat(),
                'weight_change': weight_change,
                'event_type': 'eating' if weight_change < 0 else 'food_added'
            }
        return None
    
    def log_event(self, event_data: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if event_data['event_type'] == 'eating':
                # For now, we'll log it as an unknown cat
                c.execute("""
                    INSERT INTO feeding_logs (cat_id, timestamp, amount, food_type)
                    SELECT id, ?, ?, 'Auto Detected'
                    FROM cats
                    WHERE name = 'Unknown'
                """, (event_data['timestamp'], abs(event_data['weight_change'])))
                
                # Create 'Unknown' cat if it doesn't exist
                if c.rowcount == 0:
                    c.execute("INSERT OR IGNORE INTO cats (name) VALUES ('Unknown')")
                    c.execute("""
                        INSERT INTO feeding_logs (cat_id, timestamp, amount, food_type)
                        SELECT id, ?, ?, 'Auto Detected'
                        FROM cats
                        WHERE name = 'Unknown'
                    """, (event_data['timestamp'], abs(event_data['weight_change'])))
            
            # Log raw event data for analysis
            c.execute("""
                CREATE TABLE IF NOT EXISTS sensor_logs
                (id INTEGER PRIMARY KEY,
                 timestamp TEXT,
                 event_type TEXT,
                 data TEXT)
            """)
            c.execute(
                "INSERT INTO sensor_logs (timestamp, event_type, data) VALUES (?, ?, ?)",
                (event_data['timestamp'], event_data['event_type'], json.dumps(event_data))
            )
            conn.commit()
    
    def check_alerts(self, weight: float, water_level: float):
        alerts = []
        if weight < self.config.MIN_FOOD_WEIGHT:
            alerts.append({
                'type': 'food_low',
                'message': f'Food level low: {weight:.1f}g remaining'
            })
        
        if water_level < self.config.MIN_WATER_LEVEL:
            alerts.append({
                'type': 'water_low',
                'message': f'Water level low: {water_level:.1f}%'
            })
            
        for alert in alerts:
            self.logger.warning(f"ALERT: {alert['message']}")
            # In future: send notifications (email, push, etc.)
    
    def monitoring_loop(self):
        self.running = True
        self.logger.info("Starting hardware monitoring")
        
        while self.running:
            try:
                # Measure current values
                weight = self.measure_weight()
                water_level = self.measure_water_level()
                
                # Check for significant changes
                weight_change = weight - self.last_weight
                if event := self.detect_eating(weight_change):
                    self.log_event(event)
                
                # Check for alerts
                self.check_alerts(weight, water_level)
                
                # Update last values
                self.last_weight = weight
                self.last_water_level = water_level
                
                time.sleep(self.config.SAMPLE_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    def start(self):
        self.monitor_thread = threading.Thread(target=self.monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop(self):
        self.running = False
        if HARDWARE_AVAILABLE:
            GPIO.cleanup()
    
    def get_current_status(self) -> Dict[str, Any]:
        return {
            'timestamp': datetime.now().isoformat(),
            'food_weight': self.last_weight,
            'water_level': self.last_water_level,
            'hardware_available': HARDWARE_AVAILABLE
        }

if __name__ == "__main__":
    monitor = HardwareMonitor()
    try:
        monitor.start()
        while True:
            status = monitor.get_current_status()
            print(f"\rFood: {status['food_weight']:.1f}g | Water: {status['water_level']:.1f}%", 
                  end='', flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        monitor.stop()