# MagicScript User Guide

This guide provides detailed instructions on how to use MagicScript to create and execute automated mouse and keyboard macros.

## Table of Contents

1. [Interface Overview](#interface-overview)
2. [Creating Your First Macro](#creating-your-first-macro)
3. [Action Types in Detail](#action-types-in-detail)
4. [Configuring Settings](#configuring-settings)
5. [Testing and Running Macros](#testing-and-running-macros)
6. [Tips and Best Practices](#tips-and-best-practices)
7. [Troubleshooting](#troubleshooting)

## Interface Overview

MagicScript has a simple, intuitive interface divided into two main tabs:

### Actions Tab

![Actions Tab](screenshots/actions_tab.png)

This is where you create and manage your macro actions:

- **Action List**: Displays all actions in your macro sequence
- **Add Action**: Creates a new action
- **Edit Action**: Modifies the selected action
- **Remove Action**: Deletes the selected action
- **Test Action**: Executes only the selected action
- **Test All Actions**: Runs the entire macro sequence

### Settings Tab

![Settings Tab](screenshots/settings_tab.png)

This tab contains all configuration options:

- **Idle Detection**: Configure when macros should run
- **Random Delay**: Add variability between actions
- **General Settings**: Application behavior options
- **Status**: Shows current idle time and next run information

## Creating Your First Macro

Follow these steps to create a basic macro:

### 1. Add an Action

1. Click the "Add Action" button
2. Select an action type from the dropdown menu
3. Configure the action parameters
4. Click "OK" to add the action

### 2. Build Your Sequence

Repeat the process to add multiple actions. A simple example sequence might be:

1. **Mouse Move**: Move to a specific position
2. **Mouse Click**: Perform a left click
3. **Wait**: Pause for 2 seconds
4. **Key Press**: Press a key like "Tab"

### 3. Reorder Actions

Drag and drop actions in the list to change their execution order.

### 4. Configure Idle Settings

1. Go to the "Settings" tab
2. Set your desired idle time threshold (e.g., 300 seconds = 5 minutes)
3. Ensure "Enable macro automation" is checked

### 5. Test Your Macro

Click "Test All Actions" to verify your macro works as expected.

## Action Types in Detail

### Mouse Move

![Mouse Move Dialog](screenshots/mouse_move.png)

Five movement types are available:

#### Specific Coordinates

Move the cursor to exact screen coordinates:
- **X Coordinate**: Horizontal position (0 = left edge)
- **Y Coordinate**: Vertical position (0 = top edge)
- **Duration**: How long the movement takes (in seconds)

#### Random in Range

Move to a random position within specified boundaries:
- **X Range**: Min and max horizontal boundaries
- **Y Range**: Min and max vertical boundaries
- **Duration**: How long the movement takes (in seconds)

#### Fully Random

Move to a completely random position anywhere on screen:
- **Duration**: How long the movement takes (in seconds)

#### Relative to Current Position

Move a fixed distance from the current cursor position:
- **X Offset**: Horizontal distance (positive = right, negative = left)
- **Y Offset**: Vertical distance (positive = down, negative = up)
- **Duration**: How long the movement takes (in seconds)

#### Random Range from Current Position

Move a random distance within specified ranges from current position:
- **X Offset Range**: Min and max horizontal offset
- **Y Offset Range**: Min and max vertical offset
- **Duration**: How long the movement takes (in seconds)

This option creates more natural-looking mouse movements by adding controlled randomness.

### Mouse Click

![Mouse Click Dialog](screenshots/mouse_click.png)

Perform mouse clicks:
- **Button**: Left, right, or middle mouse button
- **Clicks**: Number of clicks to perform (1-10)

### Mouse Scroll

![Mouse Scroll Dialog](screenshots/mouse_scroll.png)

Scroll the mouse wheel:

#### Fixed Amount
- **Amount**: Number of scroll clicks (positive = up, negative = down)

#### Random in Range
- **Min Amount**: Minimum scroll amount
- **Max Amount**: Maximum scroll amount

### Key Press

![Key Press Dialog](screenshots/key_press.png)

Press a single keyboard key:
- **Key**: The key to press (e.g., a, b, enter, space, tab)

### Key Combination

![Key Combination Dialog](screenshots/key_combination.png)

Press multiple keys simultaneously:
- **Keys**: Comma-separated list of keys (e.g., ctrl, alt, delete)

### Wait

![Wait Dialog](screenshots/wait.png)

Pause between actions:
- **Seconds**: Duration to wait

## Configuring Settings

### Idle Detection

- **Run macro after idle time**: Set the number of seconds of inactivity before the macro runs
- **Enable macro automation**: Turn the automation on or off

### Random Delay

- **Add random delay between actions**: Enable variable timing between actions
- **Delay range**: Set minimum and maximum delay times (in seconds)

### General Settings

- **Run on Windows startup**: Launch MagicScript when Windows starts
- **Minimize to Tray**: Hide the main window but keep the application running

## Testing and Running Macros

### Testing Individual Actions

1. Select an action from the list
2. Click "Test Action"
3. The application will briefly hide and execute just that action

### Testing the Entire Sequence

1. Click "Test All Actions"
2. The application will hide and run through all actions in order

### Running in Background

1. Configure your idle time threshold
2. Ensure "Enable macro automation" is checked
3. Click "Minimize to Tray" or close the window (the application remains in the system tray)
4. The macro will automatically run when your system has been idle for the specified time

## Tips and Best Practices

### Creating Natural-Looking Automation

- Use "Random Range from Current Position" for mouse movements
- Enable random delays between actions
- Mix different types of actions (moves, clicks, key presses)
- Add occasional wait actions

### Avoiding Detection

If you're using MagicScript to maintain activity status:
- Use small, subtle mouse movements
- Set longer idle times (5+ minutes)
- Add randomness to all actions
- Avoid repetitive patterns

### Performance Considerations

- Keep macros relatively simple
- Avoid very short idle times (< 30 seconds)
- Test thoroughly before leaving unattended

## Troubleshooting

### Application Issues

- **MagicScript won't start**: Check if it's already running in the system tray
- **High CPU usage**: Reduce the complexity of your macro or increase idle time

### Action Execution Problems

- **Mouse moves to wrong position**: Screen resolution may have changed
- **Key presses not working**: Application may be blocking input
- **Actions execute too quickly**: Add Wait actions or increase durations

### Logging

Check the log file (`magic_script.log`) in the application directory for detailed information about any errors or issues.

---

For additional help or to report bugs, please visit the [GitHub repository](https://github.com/yourusername/MagicScript/issues).