# Autoclicker App

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-green)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey)

Automated application for clicking on dynamic web elements with modern GUI interface. A collaborative project by two developers.

## 👥 Development Team

### **Core Logic & Automation**
**Kirill** - [GitHub](https://github.com/Kirill2245)
- Selenium automation engine
- Dynamic element detection algorithms
- Asynchronous task management
- Error handling system
- Browser control and optimization

### **GUI Design & Implementation**  
**Shara1b** - [GitHub](https://github.com/Shara1b)
- Modern Tkinter interface design
- Custom GUI components and styling
- Real-time console implementation
- User experience optimization
- Settings configuration panel

## 🚀 Features

- **Automatic clicking** on dynamically appearing elements
- **Smart element detection** with multiple selector fallbacks
- **Modern Graphical User Interface** with parameter configuration
- **Real-time console** with logging and command system
- **Error handling** with GUI display
- **Customizable parameters** for timeouts, retries, and CSS selectors
- **Cross-platform** compatibility (Windows, Linux, macOS)

## 🛠 Technologies

### Backend (Kirill)
- **Python 3.8+** - core programming language
- **Selenium 4** - browser automation
- **Undetected Chromedriver** - automation detection bypass
- **Asyncio** - asynchronous task execution
- **Logging** - multi-level logging system

### Frontend (Shara1b)
- **Tkinter** - graphical user interface
- **Custom GUI Components** - rounded frames, styled elements
- **Real-time console** with command processing
- **Theme management** - dark/light mode support
# 🏗️ Object-Oriented Architecture

## 🔷 Core OOP Implementation:

### **1. Class Structure:**
```python
# Main application classes
class Core:                    # Main controller class
class CoreLogic:               # Business logic handler  
class AppGUI:                  # GUI presentation layer
class LogEmitter:              # Observer pattern implementation
class RoundedFrame:            # Custom GUI component
class LogTextHandler:          # Logging handler
```

### **2. OOP Principles Applied:**

**Encapsulation:**
- Private attributes with getter/setter methods
- Data hiding through class interfaces
- Controlled access to browser instance

**Inheritance:**
- Custom GUI components inheriting from Tkinter classes
- Specialized exception classes
- Base class for common functionality

**Polymorphism:**
- Unified interface for different element types
- Plugin-based architecture for site-specific handlers
- Generic logging interface with multiple implementations

**Abstraction:**
- Abstract base classes for core functionality
- Separation of concerns between GUI and business logic
- Clean API between components

## 📦 Installation

### Method 1: Build from Source

1. **Clone the repository**:
```bash
git clone https://github.com/Kirill2245/AutoclickerApp.git
cd AutoclickerApp
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python -m gui.app_gui
```

### Method 2: Pre-built EXE (Windows)

1. **Download the latest release** from [Releases](https://github.com/Kirill2245/AutoclickerApp/releases)

2. **Run** `AutoclickerApp.exe`

## 🎮 Usage

### Basic Steps:

1. **Enter target URL** of the webpage
2. **Configure parameters**:
   - `Timeout` - element wait time (default: 0.5s)
   - `Retries` - number of click attempts (default: 3)
   - `First Click` - CSS class for primary elements
   - `Last Click` - CSS class for final elements
   - `Class Modal` - CSS class for modal windows

3. **Click "Save and Run"** to save settings and start
4. **Or click "RUN"** to start with default settings
5. **Use "STOP"** to terminate the process
6. **Use console commands** for advanced control

### ⚙️ Default Configuration:

- **URL**: http://localhost:5173/
- **Timeout**: 0.5 seconds
- **Retries**: 3 attempts
- **First Click**: `MuiTableRow-root`
- **Last Click**: `MuiButtonBase-root`
- **Class Modal**: `MuiPaper-root`

## 🎮 Console Commands

The application features a built-in console with command support:

### Available Commands:

```bash
help        # Show command help
clear       # Clear console output
test        # Test command
log_test    # Test different log levels
status      # Show process status
```

### Console Usage Example:
```
> help
Available commands:
- help: show this help
- clear: clear console
- test: test command
- log_test: test different log levels
- status: process status

> log_test
[INFO] Test information message
[WARNING] Test warning message
[ERROR] Test error message
```

## 🏗️ Architecture

### Project Structure:
```
AutoclickerApp/
├── core/           # Core logic (Kirill)
│   ├── core_main.py    # Main Core class - Browser control
│   └── core_logic.py   # Clicking logic - Element detection
├── gui/            # Graphical interface (Shara1b)
│   ├── app_gui.py      # Main window - UI layout
│   ├── styles.py       # Component styles - Theme management
│   └── components/     # Custom GUI widgets
├── emitter.py      # Event and logging system (Kirill)
├── build.py        # Build script
├── assets/         # Resources
│   └── icon.ico    # Application icon
└── requirements.txt # Dependencies
```

### Component Responsibilities:

**Kirill's Components:**
- `core_main.py` - Browser initialization and management
- `core_logic.py` - Dynamic element detection algorithms
- `emitter.py` - Event-driven logging system
- Automated error recovery system

**Shara1b's Components:**
- `app_gui.py` - Main application window and layout
- `styles.py` - Visual styling and theme management
- Custom GUI components (rounded frames, consoles)
- User interface event handling

## 🔧 Building from Source

### Create EXE File:

```bash
# Install PyInstaller
pip install pyinstaller

# Build application
python build.py

# Or manually
pyinstaller --onefile --windowed --icon=assets/icon.ico --name "AutoclickerApp" --add-data "core;core" --add-data "gui;gui" --add-data "emitter.py;." --hidden-import undetected_chromedriver --hidden-import selenium --hidden-import asyncio gui/app_gui.py
```

## 🐛 Troubleshooting

### Common Issues:

1. **Browser doesn't start**:
   - Ensure Chrome is installed
   - Check Chrome and ChromeDriver version compatibility

2. **Elements not found**:
   - Verify CSS selectors in settings
   - Increase timeout value

3. **GUI rendering issues**:
   - Ensure Python Tkinter support is installed

## 🤝 Development Process

### Collaborative Features:
- **Modular architecture** for independent development
- **Clear interfaces** between GUI and core components
- **Event-driven communication** between modules
- **Consistent coding standards** across both codebases

### Version Control:
- Feature branches for both developers
- Regular merge coordination
- Comprehensive testing before integration

## 📝 Logging System

The application supports 5 logging levels:
- `DEBUG` - debug information
- `INFO` - informational messages (default)
- `WARNING` - warnings
- `ERROR` - execution errors
- `CRITICAL` - critical errors

Logs are displayed in the GUI console and can be saved to file.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## ⭐ Support

If you find this project useful, please give it a star on GitHub!

## 🔗 Links

- **Kirill's GitHub**: https://github.com/Kirill2245
- **Shara1b's GitHub**: https://github.com/Shara1b  
- [GitHub Repository](https://github.com/Kirill2245/AutoclickerApp)
- [Issue Tracker](https://github.com/Kirill2245/AutoclickerApp/issues)
- [Releases](https://github.com/Kirill2245/AutoclickerApp/releases)

---

**Note**: This application is intended for educational and testing purposes only. Use responsibly and in compliance with website terms of service.