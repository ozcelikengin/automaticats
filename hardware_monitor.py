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
    import picamera
    import cv2
    import numpy as np
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from PIL import Image
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    
# Simple CNN for cat recognition
class CatRecognitionModel(nn.Module):
    def __init__(self, num_cats):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 80 * 60, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_cats)
        )
    
class SensorConfig:
    # HX711 pins
    HX_DATA_PIN = 5
    HX_CLOCK_PIN = 6
    
    # Water level sensor pins
    WATER_TRIG_PIN = 23
    WATER_ECHO_PIN = 24
    
    # Automatic feeder pins
    FEEDER_MOTOR_PIN = 17
    FEEDER_SENSOR_PIN = 27
    
    # Camera settings
    CAMERA_RESOLUTION = (640, 480)
    CAMERA_FRAMERATE = 30
    MODEL_PATH = 'cat_recognition_model.pth'  # Path to the trained model
    
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
            self.setup_camera()
            self.setup_feeder()
            self.load_recognition_model()
        else:
            self.logger.warning("Hardware libraries not available - running in simulation mode")
            
        self.cat_names = self.load_cat_names()
    
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
        GPIO.setup(self.config.FEEDER_MOTOR_PIN, GPIO.OUT)
        GPIO.setup(self.config.FEEDER_SENSOR_PIN, GPIO.IN)
        
        # Initialize PWM for motor control
        self.feeder_pwm = GPIO.PWM(self.config.FEEDER_MOTOR_PIN, 50)  # 50 Hz
        self.feeder_pwm.start(0)  # Start with 0% duty cycle
    
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
    
    def setup_camera(self):
        if not HARDWARE_AVAILABLE:
            return
            
        self.camera = picamera.PiCamera()
        self.camera.resolution = self.config.CAMERA_RESOLUTION
        self.camera.framerate = self.config.CAMERA_FRAMERATE
        
    def setup_feeder(self):
        if not HARDWARE_AVAILABLE:
            return
            
        # Initialize feeder position
        self.feeder_pwm.ChangeDutyCycle(0)
        
    def load_recognition_model(self):
        if not HARDWARE_AVAILABLE:
            return
            
        try:
            # Get number of cats
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM cats")
                num_cats = c.fetchone()[0]
            
            # Initialize model
            self.model = CatRecognitionModel(num_cats)
            
            # Load trained weights if available
            if os.path.exists(self.config.MODEL_PATH):
                self.model.load_state_dict(torch.load(self.config.MODEL_PATH))
                self.model.eval()
            else:
                self.logger.warning("No trained model found - cat recognition disabled")
                self.model = None
        except Exception as e:
            self.logger.error(f"Error loading recognition model: {e}")
            self.model = None
    
    def load_cat_names(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM cats")
            return {row[0]: row[1] for row in c.fetchall()}
    
    def trigger_feeding(self, amount: float) -> bool:
        if not HARDWARE_AVAILABLE:
            return False
            
        try:
            # Calculate motor run time based on amount
            run_time = amount / 10.0  # Assuming 10g/second feed rate
            
            # Start motor
            self.feeder_pwm.ChangeDutyCycle(100)
            time.sleep(run_time)
            
            # Stop motor
            self.feeder_pwm.ChangeDutyCycle(0)
            
            # Log the feeding
            self.log_event({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'automatic_feed',
                'amount': amount
            })
            
            return True
        except Exception as e:
            self.logger.error(f"Error triggering feeder: {e}")
            return False
    
    def capture_image(self):
        if not HARDWARE_AVAILABLE:
            return None
            
        try:
            # Capture to a byte stream
            stream = io.BytesIO()
            self.camera.capture(stream, format='jpeg')
            stream.seek(0)
            
            # Convert to PIL Image
            image = Image.open(stream)
            return image
        except Exception as e:
            self.logger.error(f"Error capturing image: {e}")
            return None
    
    def identify_cat(self) -> Dict[str, Any]:
        if not HARDWARE_AVAILABLE or not self.model:
            return {'success': False, 'error': 'Hardware or model not available'}
            
        try:
            # Capture image
            image = self.capture_image()
            if image is None:
                return {'success': False, 'error': 'Failed to capture image'}
            
            # Preprocess image
            transform = transforms.Compose([
                transforms.Resize((640, 480)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                  std=[0.229, 0.224, 0.225])
            ])
            
            input_tensor = transform(image).unsqueeze(0)
            
            # Get prediction
            with torch.no_grad():
                output = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)
                cat_id = torch.argmax(probabilities).item()
                confidence = probabilities[cat_id].item()
            
            # Get cat name
            cat_name = self.cat_names.get(cat_id + 1, "Unknown")  # +1 because SQLite IDs start at 1
            
            return {
                'success': True,
                'cat_name': cat_name,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in cat identification: {e}")
            return {'success': False, 'error': str(e)}
    
    def stop(self):
        self.running = False
        if HARDWARE_AVAILABLE:
            if hasattr(self, 'camera'):
                self.camera.close()
            if hasattr(self, 'feeder_pwm'):
                self.feeder_pwm.stop()
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