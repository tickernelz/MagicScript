# MagicScript - Automated Mouse and Keyboard Macro Tool

MagicScript is a Windows application that automates mouse and keyboard actions after a period of idle time. It runs in the background with a system tray icon and allows you to create custom macro sequences.

## Features

- Automatically runs macros after a configurable idle time
- Supports various actions:
  - Mouse movement:
    - Specific coordinates
    - Random in range
    - Fully random
    - Relative to current position
    - Random range from current position
  - Mouse clicks (left, right, middle)
  - Mouse scrolling:
    - Fixed amount
    - Random in range
  - Keyboard key presses
  - Keyboard key combinations
  - Wait/delay actions
- Runs in the background with system tray icon
- Single instance enforcement (prevents multiple copies running)
- Optional random delays between actions
- Option to run on Windows startup
- Beautiful and easy-to-use interface
- Configuration saved in JSON format
- Minimize to tray functionality

## Requirements

- Windows operating system
- Python 3.12 or higher
- Required Python packages (see requirements.txt)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

### Running the Application

Simply run the script:

```
python magic_script.py
```

Or use the compiled executable if available.

### Creating Macros

1. Open the application
2. Go to the "Actions" tab
3. Click "Add Action" to add a new action to your macro
4. Configure the action parameters
5. Repeat to add more actions
6. Drag and drop actions to reorder them
7. Use "Test Action" or "Test All Actions" to verify your macro

### Configuration

In the "Settings" tab, you can configure:

- Idle time before macros run
- Enable/disable macro automation
- Random delay between actions
- Run on Windows startup option

### System Tray

The application runs in the system tray. Right-click the icon to:

- Enable/disable macro automation
- Show the main window
- Quit the application

Double-click the tray icon to open the main window.

### Minimize to Tray

The application will minimize to the system tray instead of closing when you:
- Click the close (X) button
- Click the "Minimize to Tray" button in the Settings tab

This allows the application to continue running in the background.

## Building an Executable

You can build a standalone executable using PyInstaller:

```
pyinstaller --onefile --windowed --icon=icon.ico magic_script.py
```

## License

This software is provided as-is with no warranty. Use at your own risk.

## Troubleshooting

- If the application doesn't start, check if another instance is already running
- If actions don't work as expected, try testing them individually
- Check the log file (magic_script.log) for error messages

### Missing Tray Icon in Compiled Executable

If the tray icon doesn't appear when running the compiled executable:

1. Make sure both `icon.ico` and `icon.png` files are in the same directory as the executable
2. If the issue persists, try rebuilding with the provided `build.bat` script
3. As a last resort, you can manually copy the icon files to the directory where the executable is located

The application includes a fallback mechanism that will create a simple blue circle icon with "MS" text if the icon files cannot be found.