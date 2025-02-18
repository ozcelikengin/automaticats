# AutomatiCats - Smart Cat Feeding Monitor

An intelligent cat feeding monitoring system that helps track your cats' eating habits. This project combines a user-friendly GUI application with future plans for hardware integration using Raspberry Pi for automated monitoring.

## Overview

AutomatiCats helps cat owners monitor their pets' feeding patterns by:
- Tracking feeding times and amounts for multiple cats
- Recording different types of food consumption
- Providing feeding statistics and analytics
- Future support for automated monitoring using hardware sensors

## Features

### Current Features
- 🐱 Multi-cat management system
- 📝 Manual feeding log with amounts and food types
- 📊 Feeding statistics per cat
- 🕒 Timestamp tracking for all feeding events
- 💾 Persistent storage using SQLite database
- 🖥️ User-friendly GUI interface

### Planned Features
- ⚖️ Automatic weight monitoring using load cells
- 💧 Water consumption tracking
- 📱 Mobile/web interface for remote monitoring
- 📈 Advanced analytics and graphs
- 🔔 Feeding pattern alerts and notifications

## Technical Details

### Software Components
- Python-based GUI using tkinter
- SQLite database for data storage
- Modular design for easy hardware integration

### Database Schema
- `cats` table: Stores cat information
  - id (PRIMARY KEY)
  - name (UNIQUE)
- `feeding_logs` table: Records feeding events
  - id (PRIMARY KEY)
  - cat_id (FOREIGN KEY)
  - timestamp
  - amount
  - food_type

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ozcelikengin/automaticats.git
cd automaticats
```

2. Install required dependencies:
```bash
pip install tkinter
```

3. Run the application:
```bash
python cat_feeder.py
```

## Usage Guide

### Adding a New Cat
1. Enter the cat's name in the "Cat Management" section
2. Click "Add Cat"

### Logging a Feeding
1. Select the cat from the dropdown menu
2. Enter the amount of food in grams
3. Specify the food type
4. Click "Log Feeding"

### Viewing Statistics
1. The stats section shows per-cat feeding information
2. Click "Refresh Stats" to update the display
3. View total feedings, amounts, and last feeding times

## Future Hardware Implementation

### Required Components
1. Raspberry Pi (3 or 4)
2. Load Cell Components:
   - HX711 load cell amplifier
   - Weight sensor (>5kg capacity)
   - Connection wires
3. Water Monitoring:
   - Water level sensor
   - Flow meter
   - ADC converter

### Planned Sensor Integration
```
Raspberry Pi
├── Food Monitoring
│   ├── HX711 amplifier
│   └── Load cell sensor
└── Water Monitoring
    ├── Level sensor
    └── Flow meter
```

### Hardware Features
1. Food Bowl Monitoring:
   - Real-time weight measurements
   - Automatic feeding detection
   - Food level alerts

2. Water Dispenser:
   - Water level monitoring
   - Consumption tracking
   - Refill notifications

## Contributing

Contributions are welcome! Here's how you can help:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- GitHub: [@ozcelikengin](https://github.com/ozcelikengin)
- Project Link: [https://github.com/ozcelikengin/automaticats](https://github.com/ozcelikengin/automaticats)

## Acknowledgments

- Thanks to all contributors
- Inspired by the need for better pet feeding monitoring
- Special thanks to our feline friends for testing