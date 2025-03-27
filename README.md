# MagicScript

![MagicScript Logo](icon.ico)

## Overview

MagicScript is a powerful Windows automation tool that allows you to create and execute custom mouse and keyboard macros after a period of system idle time. Perfect for maintaining system activity, automating repetitive tasks, or simulating user presence.

## Features

- **Idle Detection**: Automatically triggers macros after a customizable period of system inactivity
- **Multiple Action Types**:
  - Mouse movements (absolute, relative, or random positions)
  - Mouse clicks (left, right, middle buttons with customizable click count)
  - Mouse scrolling (fixed or random amounts)
  - Keyboard key presses and key combinations
  - Wait/delay actions
- **Advanced Mouse Movement Options**:
  - Specific coordinates
  - Random position within a defined range
  - Fully random position anywhere on screen
  - Relative movement from current position
  - Random range from current position (for natural-looking movements)
- **Customizable Settings**:
  - Adjustable idle detection threshold
  - Random delays between actions
  - Run on Windows startup option
- **User-Friendly Interface**:
  - Drag-and-drop action reordering
  - System tray integration
  - Action testing capabilities
  - Visual action editor

## Installation

### Prerequisites

- Windows 10 or later
- Python 3.7 or later

### Method 1: Using the Executable (Recommended)

1. Download the latest release from the [Releases](https://github.com/yourusername/MagicScript/releases) page
2. Extract the ZIP file to your desired location
3. Run `MagicScript.exe`

### Method 2: From Source

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/MagicScript.git
   cd MagicScript
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python magic_script.py
   ```

## Usage Guide

### Getting Started

1. Launch MagicScript
2. The application will start in the system tray
3. Click the tray icon to open the main window

### Creating a Macro

1. In the "Actions" tab, click "Add Action"
2. Select an action type from the dropdown menu
3. Configure the action parameters
4. Click "OK" to add the action to your macro
5. Repeat to add more actions
6. Use drag-and-drop to reorder actions as needed

### Action Types

#### Mouse Move

Move the mouse cursor to different positions:

- **Specific Coordinates**: Move to exact X,Y screen coordinates
- **Random in Range**: Move to a random position within specified X,Y ranges
- **Fully Random**: Move to a completely random position on screen
- **Relative to Current Position**: Move a fixed distance from current position
- **Random Range from Current Position**: Move a random distance within specified ranges from current position

#### Mouse Click

Perform mouse clicks:

- Choose button type (left, right, middle)
- Set number of clicks (1-10)

#### Mouse Scroll

Scroll the mouse wheel:

- **Fixed Amount**: Scroll a specific number of clicks (positive = up, negative = down)
- **Random in Range**: Scroll a random amount between specified minimum and maximum values

#### Key Press

Press a single keyboard key:

- Enter any key name (e.g., a, b, enter, space, tab)

#### Key Combination

Press multiple keys simultaneously:

- Enter comma-separated key names (e.g., ctrl, alt, delete)

#### Wait

Pause between actions:

- Set duration in seconds

### Configuring Settings

In the "Settings" tab:

1. **Idle Detection**:
   - Set the idle time threshold (in seconds)
   - Enable/disable macro automation

2. **Random Delay**:
   - Enable/disable random delays between actions
   - Set minimum and maximum delay range (in seconds)

3. **General Settings**:
   - Enable/disable run on Windows startup
   - Minimize to tray option

### Testing Your Macro

- Select an action and click "Test Action" to test individual actions
- Click "Test All Actions" to run through the entire macro sequence

### Running in Background

- Click "Minimize to Tray" to keep the application running in the background
- The application will automatically execute your macro when the system has been idle for the specified time

## Advanced Features

### Natural Mouse Movements

The "Random Range from Current Position" option creates more natural-looking mouse movements by:

1. Keeping movements relative to the current cursor position
2. Adding randomness within specified ranges
3. Preventing large, unnatural jumps across the screen

This is particularly useful for simulating human-like activity.

### Random Delays

Enable random delays between actions to:

1. Create more natural timing patterns
2. Avoid detection by monitoring systems
3. Simulate realistic human interaction

## Troubleshooting

### Common Issues

1. **Application not starting**:
   - Ensure you have the correct permissions
   - Check if another instance is already running (look in system tray)

2. **Actions not executing**:
   - Verify that macro automation is enabled
   - Check that the idle time threshold is set appropriately
   - Ensure your actions are properly configured

3. **Mouse/keyboard actions not working**:
   - Some applications may block automated input
   - Try running MagicScript as administrator

### Logs

MagicScript creates a log file (`magic_script.log`) in the application directory. Check this file for detailed information if you encounter issues.

## Building from Source

### Creating an Executable

You can create a standalone executable using PyInstaller:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Build the executable:
   ```
   pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." magic_script.py
   ```

3. The executable will be created in the `dist` directory

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PyAutoGUI](https://pyautogui.readthedocs.io/) for mouse and keyboard automation
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework

---

Created with ❤️ by [Your Name]