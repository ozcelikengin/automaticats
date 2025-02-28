#!/usr/bin/env python3
"""
AutomatiCats Packaging Script

This script creates standalone executable versions of the AutomatiCats application
for Windows, macOS, and Linux using PyInstaller.

Usage:
    python package.py [--windows] [--macos] [--linux] [--all]

Requirements:
    - PyInstaller: pip install pyinstaller
"""

import os
import sys
import shutil
import subprocess
import argparse
import platform
from datetime import datetime

def setup_argparse():
    """Configure command line arguments"""
    parser = argparse.ArgumentParser(description='Package AutomatiCats as standalone executables')
    parser.add_argument('--windows', action='store_true', help='Build Windows executable')
    parser.add_argument('--macos', action='store_true', help='Build macOS application')
    parser.add_argument('--linux', action='store_true', help='Build Linux executable')
    parser.add_argument('--all', action='store_true', help='Build for all platforms')
    parser.add_argument('--clean', action='store_true', help='Clean build directories before packaging')
    return parser.parse_args()

def check_requirements():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("PyInstaller is installed.")
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")

def clean_directories():
    """Clean build and dist directories"""
    dirs_to_clean = ['build', 'dist']
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            print(f"Cleaning {directory}...")
            shutil.rmtree(directory)
    
    # Also remove any .spec files
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            os.remove(file)
            print(f"Removed {file}")

def create_version_file():
    """Create a version.py file with build information"""
    version = "1.0.0"  # Update as needed
    build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    build_system = platform.system()
    
    with open('version.py', 'w') as f:
        f.write(f'"""\nAutomatiCats Version Information\n"""\n\n')
        f.write(f'VERSION = "{version}"\n')
        f.write(f'BUILD_DATE = "{build_date}"\n')
        f.write(f'BUILD_SYSTEM = "{build_system}"\n')
    
    print(f"Created version.py with version {version}")
    return version

def package_windows(version):
    """Package the application for Windows"""
    print("Packaging for Windows...")
    
    # Define icon path
    icon_path = os.path.join('resources', 'icons', 'app_icon.ico')
    icon_param = f'--icon={icon_path}' if os.path.exists(icon_path) else ''
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=AutomatiCats',
        '--windowed',
        '--onefile',
        icon_param,
        '--add-data=resources;resources',
        'run.py'
    ]
    
    # Remove empty parameters
    cmd = [param for param in cmd if param]
    
    # Run PyInstaller
    subprocess.run(cmd)
    
    # Create ZIP archive
    output_dir = 'dist'
    zip_name = f'AutomatiCats-{version}-Windows.zip'
    
    # Create release directory if it doesn't exist
    if not os.path.exists('release'):
        os.makedirs('release')
    
    shutil.make_archive(
        os.path.join('release', zip_name.replace('.zip', '')),
        'zip',
        output_dir
    )
    
    print(f"Windows package created: release/{zip_name}")

def package_macos(version):
    """Package the application for macOS"""
    print("Packaging for macOS...")
    
    # Define icon path
    icon_path = os.path.join('resources', 'icons', 'app_icon.icns')
    icon_param = f'--icon={icon_path}' if os.path.exists(icon_path) else ''
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=AutomatiCats',
        '--windowed',
        '--onefile',
        icon_param,
        '--add-data=resources:resources',
        'run.py'
    ]
    
    # Remove empty parameters
    cmd = [param for param in cmd if param]
    
    # Run PyInstaller
    subprocess.run(cmd)
    
    # Create ZIP archive
    output_dir = 'dist'
    zip_name = f'AutomatiCats-{version}-macOS.zip'
    
    # Create release directory if it doesn't exist
    if not os.path.exists('release'):
        os.makedirs('release')
    
    shutil.make_archive(
        os.path.join('release', zip_name.replace('.zip', '')),
        'zip',
        output_dir
    )
    
    print(f"macOS package created: release/{zip_name}")

def package_linux(version):
    """Package the application for Linux"""
    print("Packaging for Linux...")
    
    # Define icon path
    icon_path = os.path.join('resources', 'icons', 'app_icon.png')
    icon_param = f'--icon={icon_path}' if os.path.exists(icon_path) else ''
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=AutomatiCats',
        '--windowed',
        '--onefile',
        icon_param,
        '--add-data=resources:resources',
        'run.py'
    ]
    
    # Remove empty parameters
    cmd = [param for param in cmd if param]
    
    # Run PyInstaller
    subprocess.run(cmd)
    
    # Create ZIP archive
    output_dir = 'dist'
    zip_name = f'AutomatiCats-{version}-Linux.zip'
    
    # Create release directory if it doesn't exist
    if not os.path.exists('release'):
        os.makedirs('release')
    
    shutil.make_archive(
        os.path.join('release', zip_name.replace('.zip', '')),
        'zip',
        output_dir
    )
    
    print(f"Linux package created: release/{zip_name}")

def main():
    """Main function"""
    args = setup_argparse()
    
    print("AutomatiCats Packaging Script")
    print("=============================")
    
    # Check if PyInstaller is installed
    check_requirements()
    
    # Clean directories if requested
    if args.clean:
        clean_directories()
    
    # Create version file
    version = create_version_file()
    
    # Package for selected platforms
    if args.windows or args.all:
        package_windows(version)
    
    if args.macos or args.all:
        package_macos(version)
    
    if args.linux or args.all:
        package_linux(version)
    
    # If no platform specified, package for current platform
    if not (args.windows or args.macos or args.linux or args.all):
        current_os = platform.system()
        if current_os == 'Windows':
            package_windows(version)
        elif current_os == 'Darwin':
            package_macos(version)
        elif current_os == 'Linux':
            package_linux(version)
        else:
            print(f"Unsupported platform: {current_os}")
    
    print("\nPackaging completed successfully!")
    print(f"Executable packages are available in the 'release' directory.")

if __name__ == "__main__":
    main() 