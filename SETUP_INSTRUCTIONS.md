# AutomatiCats Setup Instructions

This document provides instructions for setting up and running the AutomatiCats application, especially if you're encountering issues with PyQt6 installation on Windows.

## Quick Start

The simplest way to run the application is:

```
python run.py
```

This will:
1. Check if you have the required dependencies
2. Offer to install them if they're missing
3. Run the application

## Dependency Options

AutomatiCats can use either **PyQt6** or **PySide6** for its GUI. PySide6 is recommended for Windows users due to PyQt6 installation issues with long path names.

### Option 1: Use PySide6 (Recommended for Windows)

```
pip install PySide6
python run.py
```

If the application shows a "placeholder" interface, you'll need to convert the PyQt6 code to PySide6:

```
python convert_to_pyside6.py
python run.py
```

### Option 2: Fix PyQt6 Installation Issues on Windows

If you prefer to use PyQt6:

1. Enable long paths in Windows:
   - Run `regedit.exe` as administrator
   - Navigate to `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set the value of `LongPathsEnabled` to 1
   - Restart your computer

2. Install PyQt6:
   ```
   pip install PyQt6 --no-cache-dir
   ```

3. Run the application:
   ```
   python run.py
   ```

### Option 3: Use a Virtual Environment with Shorter Path

```
python -m venv C:\venv\automaticats
C:\venv\automaticats\Scripts\activate
pip install PyQt6
python run.py
```

## Troubleshooting

### "No module named 'PyQt6.QtWidgets'" Error

This occurs when:
- PyQt6 is not installed
- PyQt6 installation is broken due to long path issues

Solutions:
1. Switch to PySide6 using the instructions above
2. Enable long paths in Windows registry
3. Use a virtual environment with a shorter path

### "No module named 'main'" Error

This means the `main.py` file is missing or cannot be found in the current directory.

Solution:
- Make sure you're running the command from the project root directory
- Verify that `main.py` exists

### PySide6 vs PyQt6 API Differences

If you converted to PySide6 and encounter errors, there might be minor API differences:

- Change `pyqtSignal` to `Signal`
- Change `.exec()` to `.exec_()`
- Some Qt enums have different access patterns

## Files and Structure

- **run.py**: Main entry point launcher
- **main.py**: Application initialization
- **core/**: Backend functionality
- **gui/**: User interface components
- **convert_to_pyside6.py**: Utility to convert PyQt6 code to PySide6
- **install_dependencies.py**: Helper script to install dependencies

## Need Help?

If you're still having issues, contact the development team or open an issue on the project repository. 

## Recent Updates

### PySide6 Conversion Complete

The codebase has been fully converted from PyQt6 to PySide6 to address installation issues on Windows. The following changes were made:

- All PyQt6 imports have been replaced with PySide6 equivalents
- `pyqtSlot` decorators have been replaced with `Slot` decorators
- `pyqtSignal` declarations have been replaced with `Signal` declarations
- A native PySide6 fallback UI is available if needed

With these changes, the application should work out of the box with just:

```
pip install PySide6
python run.py
```

You no longer need to run the conversion script as the codebase uses PySide6 by default now. 

## Sprint 3 Update

The application has been successfully transitioned to PySide6 and is now fully working with the PySide6 UI components. All the necessary changes have been made:

- All PyQt6 imports have been replaced with PySide6 equivalents
- All `pyqtSlot` decorators have been replaced with `Slot` decorators
- All `pyqtSignal` declarations have been replaced with `Signal` declarations
- The application no longer shows the placeholder interface

To run the application, simply:

```
pip install PySide6
python run.py
```

The main application window will now load with all tabs properly functioning.

### Water Dispenser Tab Implementation

As part of Sprint 3, the Water Dispenser tab has been implemented with a prototype interface featuring:

- Status monitoring tab with water level display and manual dispense controls
- Settings tab for configuring dispensing behavior and filter management
- History tab for tracking water consumption by cat

While the interface is in place, the backend functionality will be implemented in the next sprint. The current implementation provides a visual preview of the upcoming features with placeholder data and non-functional controls (showing informative messages when clicked). 