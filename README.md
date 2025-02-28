# AutomatiCats

A desktop application for managing automated cat feeders and water dispensers.

## Features

- **Cat Management**: Register and track multiple cats with profiles
- **Feeding Schedules**: Create automated feeding schedules for each cat
- **Water Dispensing**: Track water consumption and manage water levels
- **Inventory Management**: Monitor food and water levels with low-level alerts
- **Statistics**: View feeding and hydration history with insights
- **Automated Notifications**: Receive alerts for low supplies and scheduled events

## Installation

### Prerequisites

- Python 3.8 or higher
- PyQt6
- SQLite3

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/automaticats.git
   cd automaticats
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

### Getting Started

1. **Add Cats**: First, add your cats in the "Cat Management" tab with names, weights, and optional photos
2. **Set Up Food Inventory**: Go to the "Inventory" tab to add the types of food you use
3. **Create Feeding Schedules**: In the "Feeding Schedule" tab, create feeding routines for each cat
4. **Monitor**: Check the "Statistics" tab to monitor consumption patterns

### Key Functions

- **Manual Feeding**: Use the "Feed Now" button to log manual feedings
- **Refill Supplies**: Update inventory levels when you refill food or water
- **Track Consumption**: Monitor how much each cat eats and drinks
- **Manage Schedules**: Easily enable/disable feeding schedules as needed

## Project Structure

- `core/`: Core functionality and database management
- `gui/`: User interface components
- `data/`: Storage for database and cat photos
- `logs/`: Application logs

## Development

This project follows Agile/Scrum methodology with the following planned sprints:

1. **Sprint 1**: Core architecture and database setup
2. **Sprint 2**: Basic UI and feeding functionality
3. **Sprint 3**: Notification system and multi-cat support
4. **Sprint 4**: Statistics, testing, and finalization

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Developed for all cat owners who want to ensure their feline friends are well-fed and hydrated
- Built with PyQt6 for a responsive, cross-platform desktop experience 