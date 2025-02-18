from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import sqlite3
from hardware_monitor import HardwareMonitor

app = Flask(__name__, static_folder='web')
CORS(app)

# Initialize hardware monitor
try:
    hardware_monitor = HardwareMonitor()
    hardware_monitor.start()
except Exception as e:
    print(f"Warning: Hardware initialization failed: {e}")
    hardware_monitor = None

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/api/status')
def get_status():
    if hardware_monitor:
        status = hardware_monitor.get_current_status()
    else:
        status = {
            'timestamp': datetime.now().isoformat(),
            'food_weight': 0.0,
            'water_level': 0.0,
            'hardware_available': False
        }
    return jsonify(status)

@app.route('/api/cats')
def get_cats():
    with sqlite3.connect('cat_feeder.db') as conn:
        c = conn.cursor()
        c.execute("SELECT id, name FROM cats")
        cats = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    return jsonify(cats)

@app.route('/api/feeding_logs')
def get_feeding_logs():
    days = request.args.get('days', default=7, type=int)
    since = datetime.now() - timedelta(days=days)
    
    with sqlite3.connect('cat_feeder.db') as conn:
        c = conn.cursor()
        c.execute("""
            SELECT c.name, fl.timestamp, fl.amount, fl.food_type
            FROM feeding_logs fl
            JOIN cats c ON fl.cat_id = c.id
            WHERE fl.timestamp > ?
            ORDER BY fl.timestamp DESC
        """, (since.isoformat(),))
        
        logs = [
            {
                'cat': row[0],
                'timestamp': row[1],
                'amount': row[2],
                'food_type': row[3]
            }
            for row in c.fetchall()
        ]
    return jsonify(logs)

@app.route('/api/stats')
def get_stats():
    with sqlite3.connect('cat_feeder.db') as conn:
        c = conn.cursor()
        c.execute("""
            SELECT 
                c.name,
                COUNT(*) as feeding_count,
                SUM(amount) as total_amount,
                MAX(timestamp) as last_feeding
            FROM cats c
            LEFT JOIN feeding_logs fl ON c.id = fl.cat_id
            GROUP BY c.name
        """)
        
        stats = [
            {
                'cat': row[0],
                'feeding_count': row[1],
                'total_amount': row[2],
                'last_feeding': row[3]
            }
            for row in c.fetchall()
        ]
    return jsonify(stats)

@app.route('/api/feed', methods=['POST'])
def trigger_feed():
    if not hardware_monitor:
        return jsonify({'error': 'Hardware not available'}), 400
        
    amount = request.json.get('amount', 50.0)  # Default 50g
    success = hardware_monitor.trigger_feeding(amount)
    
    return jsonify({
        'success': success,
        'message': 'Feeding triggered' if success else 'Feeding failed'
    })

@app.route('/api/camera/identify', methods=['POST'])
def identify_cat():
    if not hardware_monitor:
        return jsonify({'error': 'Hardware not available'}), 400
        
    result = hardware_monitor.identify_cat()
    return jsonify(result)

def main():
    app.run(
        host='0.0.0.0',
        port=52874,  # Use the assigned port
        debug=True
    )

if __name__ == '__main__':
    main()