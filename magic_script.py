#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MagicScript - Automated Mouse and Keyboard Macro Tool
A Windows application that automates mouse and keyboard actions after a period of idle time.
"""

import sys
import os
import json
import time
import random
import ctypes
from ctypes import wintypes
import threading
import logging
from datetime import datetime
from enum import Enum, auto
import pyautogui
import PyQt6.sip
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QEvent, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPalette, QDrag, QPixmap, QPainter
from PyQt6.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu,
                             QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSpinBox, QListWidget, QListWidgetItem, QComboBox,
                             QMessageBox, QDialog, QDialogButtonBox, QLineEdit,
                             QGroupBox, QFormLayout, QTabWidget, QCheckBox, QSlider, QDoubleSpinBox)

# Function to get correct resource path for both development and PyInstaller
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)
    if not os.path.exists(path):
        logging.warning(f"Resource not found: {path}")
        # Try alternate locations
        alt_paths = [
            os.path.join(os.path.dirname(sys.executable), relative_path),
            os.path.join(os.getcwd(), relative_path)
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                logging.info(f"Found resource at alternate location: {alt_path}")
                return alt_path

    return path

# Constants
APP_NAME = "MagicScript"
APP_VERSION = "1.0.0"
CONFIG_FILE = "magic_script_config.json"
DEFAULT_IDLE_TIME = 300  # 5 minutes in seconds
MUTEX_NAME = "Global\\MagicScript_SingleInstance_Mutex"

# Setup logging
log_file = "magic_script.log"
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture more information
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MagicScript")

# Add exception hook to catch unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set the exception hook
sys.excepthook = handle_exception

logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
logger.info(f"Log file: {os.path.abspath(log_file)}")

# Windows API for idle time detection
class LastInputInfo(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.c_uint),
        ('dwTime', ctypes.c_uint),
    ]

# Action types
class ActionType(Enum):
    MOUSE_MOVE = auto()
    MOUSE_CLICK = auto()
    MOUSE_SCROLL = auto()
    KEY_PRESS = auto()
    KEY_COMBINATION = auto()
    WAIT = auto()

# Single instance check using Windows mutex
def ensure_single_instance():
    try:
        mutex = ctypes.windll.kernel32.CreateMutexW(None, 1, MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            QMessageBox.warning(
                None, 
                "Already Running", 
                f"{APP_NAME} is already running.\nCheck the system tray for the icon."
            )
            sys.exit(0)
        return mutex
    except Exception as e:
        logger.error(f"Error creating mutex: {e}")
        return None

# Get idle time in milliseconds
def get_idle_time():
    last_input_info = LastInputInfo()
    last_input_info.cbSize = ctypes.sizeof(last_input_info)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
    millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis / 1000.0  # Convert to seconds

# Action class to represent a macro action
class Action:
    def __init__(self, action_type, params=None, name=None):
        self.action_type = action_type
        self.params = params or {}
        self.name = name or self.generate_name()
        
    def generate_name(self):
        if self.action_type == ActionType.MOUSE_MOVE:
            move_type = self.params.get('move_type', 0)
            if move_type == 0:  # Specific Coordinates
                return f"Move mouse to ({self.params.get('x', 0)}, {self.params.get('y', 0)})"
            elif move_type == 1:  # Random in Range
                return f"Move mouse randomly in range X:{self.params.get('x_min', 0)}-{self.params.get('x_max', 1000)}, Y:{self.params.get('y_min', 0)}-{self.params.get('y_max', 1000)}"
            elif move_type == 3:  # Relative to Current Position
                x_offset = self.params.get('x_offset', 50)
                y_offset = self.params.get('y_offset', 50)
                direction_x = "right" if x_offset >= 0 else "left"
                direction_y = "down" if y_offset >= 0 else "up"
                return f"Move mouse {abs(x_offset)}px {direction_x}, {abs(y_offset)}px {direction_y} from current position"
            elif move_type == 4:  # Random Range from Current Position
                x_min = self.params.get('x_offset_min', -50)
                x_max = self.params.get('x_offset_max', 50)
                y_min = self.params.get('y_offset_min', -50)
                y_max = self.params.get('y_offset_max', 50)
                return f"Move mouse randomly within offset range X:{x_min} to {x_max}, Y:{y_min} to {y_max} from current position"
            else:  # Fully Random
                return "Move mouse to random position"

        elif self.action_type == ActionType.MOUSE_CLICK:
            return f"Mouse {self.params.get('button', 'left')} click ({self.params.get('clicks', 1)} clicks)"

        elif self.action_type == ActionType.MOUSE_SCROLL:
            scroll_type = self.params.get('scroll_type', 0)
            if scroll_type == 0:  # Fixed Amount
                return f"Scroll {self.params.get('amount', 0)} clicks"
            else:  # Random in Range
                return f"Scroll randomly between {self.params.get('min_amount', -20)} and {self.params.get('max_amount', 20)} clicks"

        elif self.action_type == ActionType.KEY_PRESS:
            return f"Press {self.params.get('key', '')}"

        elif self.action_type == ActionType.KEY_COMBINATION:
            return f"Press {'+'.join(self.params.get('keys', []))}"

        elif self.action_type == ActionType.WAIT:
            return f"Wait {self.params.get('seconds', 1)} seconds"

        return "Unknown action"
    
    def execute(self):
        try:
            # Wrap the entire execution in a try-except to catch any unexpected errors
            try:
                if self.action_type == ActionType.MOUSE_MOVE:
                    duration = self.params.get('duration', 0.5)
                    move_type = self.params.get('move_type', 0)

                    logger.debug(f"Executing mouse move action with type {move_type} and params: {self.params}")

                    # Determine coordinates based on movement type
                    if move_type == 0:  # Specific Coordinates
                        x = self.params.get('x', 500)
                        y = self.params.get('y', 500)
                        logger.info(f"Moving mouse to absolute position ({x}, {y}) with duration {duration}")
                        pyautogui.moveTo(x, y, duration=duration)

                    elif move_type == 1:  # Random in Range
                        x_min = self.params.get('x_min', 0)
                        x_max = self.params.get('x_max', 1000)
                        y_min = self.params.get('y_min', 0)
                        y_max = self.params.get('y_max', 1000)

                        # Ensure min <= max
                        if x_min > x_max:
                            x_min, x_max = x_max, x_min
                        if y_min > y_max:
                            y_min, y_max = y_max, y_min

                        x = random.randint(x_min, x_max)
                        y = random.randint(y_min, y_max)
                        logger.info(f"Moving mouse to random position in range ({x}, {y}) with duration {duration}")
                        pyautogui.moveTo(x, y, duration=duration)

                    elif move_type == 3:  # Relative to Current Position
                        x_offset = self.params.get('x_offset', 50)
                        y_offset = self.params.get('y_offset', 50)
                        current_x, current_y = pyautogui.position()
                        new_x = current_x + x_offset
                        new_y = current_y + y_offset
                        logger.info(f"Moving mouse from ({current_x}, {current_y}) to relative position ({new_x}, {new_y}) with offset ({x_offset}, {y_offset})")
                        pyautogui.moveRel(x_offset, y_offset, duration=duration)

                    elif move_type == 4:  # Random Range from Current Position
                        # Get parameters with defaults
                        x_offset_min = int(self.params.get('x_offset_min', -50))
                        x_offset_max = int(self.params.get('x_offset_max', 50))
                        y_offset_min = int(self.params.get('y_offset_min', -50))
                        y_offset_max = int(self.params.get('y_offset_max', 50))

                        # Ensure min <= max
                        if x_offset_min > x_offset_max:
                            x_offset_min, x_offset_max = x_offset_max, x_offset_min
                        if y_offset_min > y_offset_max:
                            y_offset_min, y_offset_max = y_offset_max, y_offset_min

                        # Log the parameters for debugging
                        logger.debug(f"Random range parameters: X: {x_offset_min}-{x_offset_max}, Y: {y_offset_min}-{y_offset_max}")

                        # Generate random offsets
                        x_offset = random.randint(x_offset_min, x_offset_max)
                        y_offset = random.randint(y_offset_min, y_offset_max)

                        # Get current position
                        current_x, current_y = pyautogui.position()
                        new_x = current_x + x_offset
                        new_y = current_y + y_offset

                        logger.info(f"Moving mouse from ({current_x}, {current_y}) to random relative position ({new_x}, {new_y}) with offset ({x_offset}, {y_offset})")
                        pyautogui.moveRel(x_offset, y_offset, duration=duration)

                    else:  # Fully Random
                        screen_width, screen_height = pyautogui.size()
                        x = random.randint(0, screen_width)
                        y = random.randint(0, screen_height)
                        logger.info(f"Moving mouse to fully random position ({x}, {y}) with duration {duration}")
                        pyautogui.moveTo(x, y, duration=duration)

                elif self.action_type == ActionType.MOUSE_CLICK:
                    button = self.params.get('button', 'left')
                    clicks = self.params.get('clicks', 1)
                    logger.info(f"Clicking mouse button {button} {clicks} times")
                    pyautogui.click(button=button, clicks=clicks)

                elif self.action_type == ActionType.MOUSE_SCROLL:
                    scroll_type = self.params.get('scroll_type', 0)

                    if scroll_type == 0:  # Fixed Amount
                        amount = self.params.get('amount', 0)
                    else:  # Random in Range
                        min_amount = self.params.get('min_amount', -20)
                        max_amount = self.params.get('max_amount', 20)

                        # Ensure min <= max
                        if min_amount > max_amount:
                            min_amount, max_amount = max_amount, min_amount

                        amount = random.randint(min_amount, max_amount)

                    logger.info(f"Scrolling mouse by {amount} clicks")
                    pyautogui.scroll(amount)

                elif self.action_type == ActionType.KEY_PRESS:
                    key = self.params.get('key', '')
                    if key:
                        logger.info(f"Pressing key: {key}")
                        pyautogui.press(key)

                elif self.action_type == ActionType.KEY_COMBINATION:
                    keys = self.params.get('keys', [])
                    if keys:
                        logger.info(f"Pressing key combination: {'+'.join(keys)}")
                        pyautogui.hotkey(*keys)

                elif self.action_type == ActionType.WAIT:
                    seconds = self.params.get('seconds', 1)
                    logger.info(f"Waiting for {seconds} seconds")
                    time.sleep(seconds)

                return True

            except Exception as e:
                # Catch and log any unexpected errors during execution
                logger.error(f"Unexpected error executing action {self.name}: {e}", exc_info=True)
                return False

        except Exception as e:
            # This is a fallback in case the inner try-except fails
            logger.critical(f"Critical error in execute method: {e}", exc_info=True)
            return False
    
    def to_dict(self):
        return {
            'action_type': self.action_type.name,
            'params': self.params,
            'name': self.name
        }
    
    @classmethod
    def from_dict(cls, data):
        try:
            # Handle string or enum action_type
            if isinstance(data.get('action_type'), str):
                action_type = ActionType[data['action_type']]
            elif isinstance(data.get('action_type'), ActionType):
                action_type = data['action_type']
            else:
                logger.error(f"Invalid action_type in data: {data.get('action_type')}")
                # Default to WAIT as a safe fallback
                action_type = ActionType.WAIT

            # Get params with fallback to empty dict
            params = data.get('params', {})

            # Get name with fallback to None (will generate name)
            name = data.get('name')

            return cls(action_type, params, name)
        except Exception as e:
            logger.error(f"Error creating Action from dict: {e}, data: {data}")
            # Return a safe default action
            return cls(ActionType.WAIT, {'seconds': 1}, "Error recovery action")


# Configuration manager
class ConfigManager:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
        # Ensure actions are properly converted to Action objects
        self._normalize_actions()
        
    def load_config(self):
        default_config = {
            'idle_time': DEFAULT_IDLE_TIME,
            'actions': [],
            'enabled': True,
            'run_on_startup': False,
            'random_delay': False,
            'random_delay_min': 0,
            'random_delay_max': 30
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Ensure all default keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            
        return default_config
    
    def save_config(self):
        try:
            # Convert actions to serializable format
            config_copy = self.config.copy()
            if 'actions' in config_copy:
                serialized_actions = []
                for action in config_copy['actions']:
                    if isinstance(action, Action):
                        serialized_actions.append(action.to_dict())
                    elif isinstance(action, dict):
                        # If it's already a dict, keep it as is
                        serialized_actions.append(action)
                    else:
                        logger.warning(f"Unknown action type: {type(action)}")

                config_copy['actions'] = serialized_actions

            with open(self.config_file, 'w') as f:
                json.dump(config_copy, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get_actions(self):
        actions = []
        for action_data in self.config.get('actions', []):
            try:
                if isinstance(action_data, dict):
                    # Convert dictionary to Action object
                    actions.append(Action.from_dict(action_data))
                elif isinstance(action_data, Action):
                    # Already an Action object
                    actions.append(action_data)
                else:
                    logger.warning(f"Skipping unknown action type: {type(action_data)}")
            except Exception as e:
                logger.error(f"Error loading action: {e}")
        return actions
    
    def set_actions(self, actions):
        self.config['actions'] = actions
        self.save_config()
    
    def get_idle_time(self):
        return self.config.get('idle_time', DEFAULT_IDLE_TIME)
    
    def set_idle_time(self, seconds):
        self.config['idle_time'] = seconds
        self.save_config()
    
    def is_enabled(self):
        return self.config.get('enabled', True)
    
    def set_enabled(self, enabled):
        self.config['enabled'] = enabled
        self.save_config()
    
    def get_run_on_startup(self):
        return self.config.get('run_on_startup', False)
    
    def set_run_on_startup(self, enabled):
        self.config['run_on_startup'] = enabled
        self.save_config()
        self._update_startup_registry(enabled)
    
    def _update_startup_registry(self, enabled):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            if enabled:
                executable = sys.executable
                if executable.endswith('python.exe'):
                    # Running as script
                    script_path = os.path.abspath(sys.argv[0])
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{executable}" "{script_path}"')
                else:
                    # Running as exe
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{executable}"')
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
            
            winreg.CloseKey(key)
        except Exception as e:
            logger.error(f"Error updating startup registry: {e}")
    
    def get_random_delay(self):
        return self.config.get('random_delay', False)
    
    def set_random_delay(self, enabled):
        self.config['random_delay'] = enabled
        self.save_config()
    
    def get_random_delay_range(self):
        min_delay = self.config.get('random_delay_min', 0)
        max_delay = self.config.get('random_delay_max', 30)
        return min_delay, max_delay
    
    def set_random_delay_range(self, min_delay, max_delay):
        self.config['random_delay_min'] = min_delay
        self.config['random_delay_max'] = max_delay
        self.save_config()

    def _normalize_actions(self):
        """Ensure all actions in the config are properly converted to Action objects"""
        if 'actions' in self.config:
            # Get actions as Action objects
            actions = self.get_actions()
            # Store them back in the config
            self.config['actions'] = actions
            # No need to save here as this is just normalizing the in-memory representation


# Custom list widget item for actions
class ActionListWidgetItem(QListWidgetItem):
    def __init__(self, action, parent=None):
        super().__init__(action.name, parent)
        self.action = action
        self.setToolTip(self._generate_tooltip())
    
    def _generate_tooltip(self):
        action_type = self.action.action_type.name.replace('_', ' ').title()
        params = ', '.join([f"{k}: {v}" for k, v in self.action.params.items()])
        return f"Type: {action_type}\nParameters: {params}"


# Dialog for adding/editing actions
class ActionDialog(QDialog):
    def __init__(self, parent=None, action=None):
        super().__init__(parent)
        self.action = action
        self.setWindowTitle("Add Action" if action is None else "Edit Action")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Action type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Action Type:"))
        self.type_combo = QComboBox()
        for action_type in ActionType:
            self.type_combo.addItem(action_type.name.replace('_', ' ').title(), action_type)
        self.type_combo.currentIndexChanged.connect(self.on_action_type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Parameters group
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QFormLayout()
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)

        # Initialize with current action if editing, otherwise show default parameters
        if self.action:
            index = self.type_combo.findData(self.action.action_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            self.on_action_type_changed()
            self.populate_params()
        else:
            # Show default parameters for first action type
            self.on_action_type_changed()
    
    def on_action_type_changed(self):
        # Clear previous parameters
        while self.params_layout.rowCount() > 0:
            self.params_layout.removeRow(0)
        
        action_type = self.type_combo.currentData()
        
        if action_type == ActionType.MOUSE_MOVE:
            # Movement type
            self.move_type_combo = QComboBox()
            self.move_type_combo.addItems([
                "Specific Coordinates",
                "Random in Range",
                "Fully Random",
                "Relative to Current Position",
                "Random Range from Current Position"
            ])
            self.move_type_combo.currentIndexChanged.connect(self._update_mouse_move_ui)
            self.params_layout.addRow("Movement Type:", self.move_type_combo)

            # Coordinates group
            self.coords_group = QGroupBox("Coordinates")
            coords_layout = QFormLayout()

            # X coordinate
            self.x_spin = QSpinBox()
            self.x_spin.setRange(0, 9999)
            self.x_spin.setValue(500)
            self.x_label = QLabel("X Coordinate:")
            coords_layout.addRow(self.x_label, self.x_spin)

            # Y coordinate
            self.y_spin = QSpinBox()
            self.y_spin.setRange(0, 9999)
            self.y_spin.setValue(500)
            self.y_label = QLabel("Y Coordinate:")
            coords_layout.addRow(self.y_label, self.y_spin)

            # X range
            range_x_layout = QHBoxLayout()
            self.x_min_spin = QSpinBox()
            self.x_min_spin.setRange(0, 9999)
            self.x_min_spin.setValue(0)
            self.x_max_spin = QSpinBox()
            self.x_max_spin.setRange(0, 9999)
            self.x_max_spin.setValue(1000)
            range_x_layout.addWidget(QLabel("Min:"))
            range_x_layout.addWidget(self.x_min_spin)
            range_x_layout.addWidget(QLabel("Max:"))
            range_x_layout.addWidget(self.x_max_spin)
            self.x_range_label = QLabel("X Range:")
            coords_layout.addRow(self.x_range_label, range_x_layout)

            # Y range
            range_y_layout = QHBoxLayout()
            self.y_min_spin = QSpinBox()
            self.y_min_spin.setRange(0, 9999)
            self.y_min_spin.setValue(0)
            self.y_max_spin = QSpinBox()
            self.y_max_spin.setRange(0, 9999)
            self.y_max_spin.setValue(1000)
            range_y_layout.addWidget(QLabel("Min:"))
            range_y_layout.addWidget(self.y_min_spin)
            range_y_layout.addWidget(QLabel("Max:"))
            range_y_layout.addWidget(self.y_max_spin)
            self.y_range_label = QLabel("Y Range:")
            coords_layout.addRow(self.y_range_label, range_y_layout)

            self.coords_group.setLayout(coords_layout)
            self.params_layout.addRow("", self.coords_group)

            # Duration
            self.duration_spin = QDoubleSpinBox()
            self.duration_spin.setRange(0.1, 10.0)
            self.duration_spin.setValue(0.5)
            self.duration_spin.setSingleStep(0.1)
            self.params_layout.addRow("Duration (seconds):", self.duration_spin)

            # Initialize UI based on movement type
            self._update_mouse_move_ui()
            
        elif action_type == ActionType.MOUSE_CLICK:
            # Button
            self.button_combo = QComboBox()
            self.button_combo.addItems(["left", "right", "middle"])
            self.params_layout.addRow("Button:", self.button_combo)
            
            # Clicks
            self.clicks_spin = QSpinBox()
            self.clicks_spin.setRange(1, 10)
            self.clicks_spin.setValue(1)
            self.params_layout.addRow("Clicks:", self.clicks_spin)
            
        elif action_type == ActionType.MOUSE_SCROLL:
            # Scroll type
            self.scroll_type_combo = QComboBox()
            self.scroll_type_combo.addItems(["Fixed Amount", "Random in Range"])
            self.scroll_type_combo.currentIndexChanged.connect(self._update_scroll_ui)
            self.params_layout.addRow("Scroll Type:", self.scroll_type_combo)

            # Fixed amount
            self.amount_spin = QSpinBox()
            self.amount_spin.setRange(-100, 100)
            self.amount_spin.setValue(10)
            self.params_layout.addRow("Amount (+ up, - down):", self.amount_spin)

            # Random range
            range_layout = QHBoxLayout()
            self.min_amount_spin = QSpinBox()
            self.min_amount_spin.setRange(-100, 100)
            self.min_amount_spin.setValue(-20)
            self.max_amount_spin = QSpinBox()
            self.max_amount_spin.setRange(-100, 100)
            self.max_amount_spin.setValue(20)
            range_layout.addWidget(QLabel("Min:"))
            range_layout.addWidget(self.min_amount_spin)
            range_layout.addWidget(QLabel("Max:"))
            range_layout.addWidget(self.max_amount_spin)
            self.range_row = self.params_layout.addRow("Range:", range_layout)

            # Initialize UI based on scroll type
            self._update_scroll_ui()
            
        elif action_type == ActionType.KEY_PRESS:
            # Key
            self.key_edit = QLineEdit()
            self.key_edit.setPlaceholderText("e.g. a, b, enter, space, tab, etc.")
            self.params_layout.addRow("Key:", self.key_edit)
            
        elif action_type == ActionType.KEY_COMBINATION:
            # Keys
            self.keys_edit = QLineEdit()
            self.keys_edit.setPlaceholderText("e.g. ctrl, alt, delete (comma separated)")
            self.params_layout.addRow("Keys (comma separated):", self.keys_edit)
            
        elif action_type == ActionType.WAIT:
            # Seconds
            self.seconds_spin = QDoubleSpinBox()
            self.seconds_spin.setRange(0.1, 60.0)
            self.seconds_spin.setValue(1.0)
            self.seconds_spin.setSingleStep(0.1)
            self.params_layout.addRow("Seconds:", self.seconds_spin)
    
    def _update_mouse_move_ui(self, index=None):
        """Update the mouse move UI based on the selected movement type"""
        try:
            if index is None:
                index = self.move_type_combo.currentIndex()

            # Show/hide appropriate controls based on movement type
            if index == 0:  # Specific Coordinates
                self.x_spin.setVisible(True)
                self.y_spin.setVisible(True)
                self.x_min_spin.setVisible(False)
                self.x_max_spin.setVisible(False)
                self.y_min_spin.setVisible(False)
                self.y_max_spin.setVisible(False)

                # Update labels for absolute coordinates
                self.x_label.setText("X Coordinate:")
                self.y_label.setText("Y Coordinate:")

            elif index == 1:  # Random in Range
                self.x_spin.setVisible(False)
                self.y_spin.setVisible(False)
                self.x_min_spin.setVisible(True)
                self.x_max_spin.setVisible(True)
                self.y_min_spin.setVisible(True)
                self.y_max_spin.setVisible(True)

                # Update labels for absolute range
                self.x_range_label.setText("X Range:")
                self.y_range_label.setText("Y Range:")

            elif index == 3:  # Relative to Current Position
                self.x_spin.setVisible(True)
                self.y_spin.setVisible(True)
                self.x_min_spin.setVisible(False)
                self.x_max_spin.setVisible(False)
                self.y_min_spin.setVisible(False)
                self.y_max_spin.setVisible(False)

                # Update labels for relative coordinates
                self.x_label.setText("X Offset:")
                self.y_label.setText("Y Offset:")

                # Allow negative values for relative movement
                self.x_spin.setRange(-9999, 9999)
                self.y_spin.setRange(-9999, 9999)

                # Set default values to small offsets
                if self.x_spin.value() == 500 and self.y_spin.value() == 500:
                    self.x_spin.setValue(50)
                    self.y_spin.setValue(50)

            elif index == 4:  # Random Range from Current Position
                self.x_spin.setVisible(False)
                self.y_spin.setVisible(False)
                self.x_min_spin.setVisible(True)
                self.x_max_spin.setVisible(True)
                self.y_min_spin.setVisible(True)
                self.y_max_spin.setVisible(True)

                # Update labels for relative range
                self.x_range_label.setText("X Offset Range:")
                self.y_range_label.setText("Y Offset Range:")

                # Allow negative values for relative range
                self.x_min_spin.setRange(-9999, 9999)
                self.x_max_spin.setRange(-9999, 9999)
                self.y_min_spin.setRange(-9999, 9999)
                self.y_max_spin.setRange(-9999, 9999)

                # Set default values to small offset ranges
                if self.x_min_spin.value() == 0 and self.x_max_spin.value() == 1000:
                    self.x_min_spin.setValue(-50)
                    self.x_max_spin.setValue(50)
                    self.y_min_spin.setValue(-50)
                    self.y_max_spin.setValue(50)

            else:  # Fully Random
                self.coords_group.setVisible(False)
                return

            self.coords_group.setVisible(True)

        except Exception as e:
            logger.error(f"Error in _update_mouse_move_ui: {e}", exc_info=True)
            # Don't crash the application, just show the error
            QMessageBox.warning(None, "Error", f"Error updating UI: {str(e)}")

    def _update_scroll_ui(self, index=None):
        """Update the scroll UI based on the selected scroll type"""
        if index is None:
            index = self.scroll_type_combo.currentIndex()

        # Show/hide appropriate controls based on scroll type
        if index == 0:  # Fixed Amount
            self.amount_spin.setVisible(True)
            self.min_amount_spin.setVisible(False)
            self.max_amount_spin.setVisible(False)
        else:  # Random in Range
            self.amount_spin.setVisible(False)
            self.min_amount_spin.setVisible(True)
            self.max_amount_spin.setVisible(True)

    def populate_params(self):
        action_type = self.action.action_type
        params = self.action.params

        if action_type == ActionType.MOUSE_MOVE:
            # Set movement type
            move_type = params.get('move_type', 0)
            self.move_type_combo.setCurrentIndex(move_type)

            if move_type == 0:  # Specific Coordinates
                if 'x' in params:
                    self.x_spin.setValue(params['x'] if params['x'] is not None else 500)
                if 'y' in params:
                    self.y_spin.setValue(params['y'] if params['y'] is not None else 500)
            elif move_type == 1:  # Random in Range
                if 'x_min' in params:
                    self.x_min_spin.setValue(params['x_min'])
                if 'x_max' in params:
                    self.x_max_spin.setValue(params['x_max'])
                if 'y_min' in params:
                    self.y_min_spin.setValue(params['y_min'])
                if 'y_max' in params:
                    self.y_max_spin.setValue(params['y_max'])
            elif move_type == 3:  # Relative to Current Position
                if 'x_offset' in params:
                    self.x_spin.setValue(params['x_offset'])
                if 'y_offset' in params:
                    self.y_spin.setValue(params['y_offset'])
            elif move_type == 4:  # Random Range from Current Position
                if 'x_offset_min' in params:
                    self.x_min_spin.setValue(params['x_offset_min'])
                if 'x_offset_max' in params:
                    self.x_max_spin.setValue(params['x_offset_max'])
                if 'y_offset_min' in params:
                    self.y_min_spin.setValue(params['y_offset_min'])
                if 'y_offset_max' in params:
                    self.y_max_spin.setValue(params['y_offset_max'])

            if 'duration' in params:
                self.duration_spin.setValue(params['duration'])

        elif action_type == ActionType.MOUSE_CLICK:
            if 'button' in params:
                index = self.button_combo.findText(params['button'])
                if index >= 0:
                    self.button_combo.setCurrentIndex(index)
            if 'clicks' in params:
                self.clicks_spin.setValue(params['clicks'])

        elif action_type == ActionType.MOUSE_SCROLL:
            # Set scroll type
            scroll_type = params.get('scroll_type', 0)
            self.scroll_type_combo.setCurrentIndex(scroll_type)

            if scroll_type == 0:  # Fixed Amount
                if 'amount' in params:
                    self.amount_spin.setValue(params['amount'])
            else:  # Random in Range
                if 'min_amount' in params:
                    self.min_amount_spin.setValue(params['min_amount'])
                if 'max_amount' in params:
                    self.max_amount_spin.setValue(params['max_amount'])

        elif action_type == ActionType.KEY_PRESS:
            if 'key' in params:
                self.key_edit.setText(params['key'])

        elif action_type == ActionType.KEY_COMBINATION:
            if 'keys' in params:
                self.keys_edit.setText(', '.join(params['keys']))

        elif action_type == ActionType.WAIT:
            if 'seconds' in params:
                self.seconds_spin.setValue(params['seconds'])
    
    def get_params(self):
        action_type = self.type_combo.currentData()
        params = {}

        if action_type == ActionType.MOUSE_MOVE:
            move_type = self.move_type_combo.currentIndex()
            params['move_type'] = move_type

            if move_type == 0:  # Specific Coordinates
                params['x'] = self.x_spin.value()
                params['y'] = self.y_spin.value()
            elif move_type == 1:  # Random in Range
                params['x_min'] = self.x_min_spin.value()
                params['x_max'] = self.x_max_spin.value()
                params['y_min'] = self.y_min_spin.value()
                params['y_max'] = self.y_max_spin.value()
            elif move_type == 3:  # Relative to Current Position
                params['x_offset'] = self.x_spin.value()
                params['y_offset'] = self.y_spin.value()
            elif move_type == 4:  # Random Range from Current Position
                params['x_offset_min'] = self.x_min_spin.value()
                params['x_offset_max'] = self.x_max_spin.value()
                params['y_offset_min'] = self.y_min_spin.value()
                params['y_offset_max'] = self.y_max_spin.value()
            # For fully random, no additional parameters needed

            params['duration'] = self.duration_spin.value()

        elif action_type == ActionType.MOUSE_CLICK:
            params['button'] = self.button_combo.currentText()
            params['clicks'] = self.clicks_spin.value()

        elif action_type == ActionType.MOUSE_SCROLL:
            scroll_type = self.scroll_type_combo.currentIndex()
            params['scroll_type'] = scroll_type

            if scroll_type == 0:  # Fixed Amount
                params['amount'] = self.amount_spin.value()
            else:  # Random in Range
                params['min_amount'] = self.min_amount_spin.value()
                params['max_amount'] = self.max_amount_spin.value()

        elif action_type == ActionType.KEY_PRESS:
            params['key'] = self.key_edit.text().strip()

        elif action_type == ActionType.KEY_COMBINATION:
            keys_text = self.keys_edit.text()
            params['keys'] = [k.strip() for k in keys_text.split(',') if k.strip()]

        elif action_type == ActionType.WAIT:
            params['seconds'] = self.seconds_spin.value()

        return params
    
    def accept(self):
        try:
            action_type = self.type_combo.currentData()
            params = self.get_params()

            # Validate parameters
            if action_type == ActionType.KEY_PRESS and not params.get('key'):
                QMessageBox.warning(self, "Validation Error", "Please enter a key.")
                return

            if action_type == ActionType.KEY_COMBINATION and not params.get('keys'):
                QMessageBox.warning(self, "Validation Error", "Please enter at least one key.")
                return

            # Additional validation for random ranges
            if action_type == ActionType.MOUSE_MOVE:
                move_type = params.get('move_type')

                # Validate Random in Range
                if move_type == 1:
                    x_min = params.get('x_min', 0)
                    x_max = params.get('x_max', 1000)
                    y_min = params.get('y_min', 0)
                    y_max = params.get('y_max', 1000)

                    if x_min > x_max:
                        QMessageBox.warning(self, "Validation Error", "X minimum must be less than or equal to X maximum.")
                        return

                    if y_min > y_max:
                        QMessageBox.warning(self, "Validation Error", "Y minimum must be less than or equal to Y maximum.")
                        return

                # Validate Random Range from Current Position
                elif move_type == 4:
                    x_min = params.get('x_offset_min', -50)
                    x_max = params.get('x_offset_max', 50)
                    y_min = params.get('y_offset_min', -50)
                    y_max = params.get('y_offset_max', 50)

                    if x_min > x_max:
                        QMessageBox.warning(self, "Validation Error", "X offset minimum must be less than or equal to X offset maximum.")
                        return

                    if y_min > y_max:
                        QMessageBox.warning(self, "Validation Error", "Y offset minimum must be less than or equal to Y offset maximum.")
                        return

            # Validate scroll ranges
            if action_type == ActionType.MOUSE_SCROLL:
                scroll_type = params.get('scroll_type')
                if scroll_type == 1:  # Random in Range
                    min_amount = params.get('min_amount', -20)
                    max_amount = params.get('max_amount', 20)

                    if min_amount > max_amount:
                        QMessageBox.warning(self, "Validation Error", "Scroll minimum must be less than or equal to scroll maximum.")
                        return

            # Create or update action
            try:
                if self.action:
                    # Update existing action
                    self.action.action_type = action_type
                    self.action.params = params
                    self.action.name = self.action.generate_name()
                else:
                    # Create new action
                    self.action = Action(action_type, params)

                # Test if the action can generate a name without errors
                test_name = self.action.generate_name()
                logger.debug(f"Generated action name: {test_name}")

                super().accept()
            except Exception as e:
                logger.error(f"Error creating/updating action: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to create action: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error in accept method: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")


# Main application window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.actions = self.config_manager.get_actions()
        self.setup_ui()
        self.setup_tray()
        self.setup_macro_engine()
        
        # Apply settings
        self.idle_spin.setValue(self.config_manager.get_idle_time())
        self.enabled_check.setChecked(self.config_manager.is_enabled())
        self.startup_check.setChecked(self.config_manager.get_run_on_startup())
        self.random_delay_check.setChecked(self.config_manager.get_random_delay())
        min_delay, max_delay = self.config_manager.get_random_delay_range()
        self.min_delay_spin.setValue(min_delay)
        self.max_delay_spin.setValue(max_delay)
        
        # Update UI state
        self.update_action_list()
        self.update_controls_state()
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")

        # Try to load the icon, with fallbacks
        icon_path = resource_path("icon.ico")
        if not os.path.exists(icon_path):
            # Try PNG version
            icon_path = resource_path("icon.png")

        if os.path.exists(icon_path):
            logger.info(f"Loading window icon from: {icon_path}")
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Create a simple fallback icon if no icon file is found
            logger.warning("Icon files not found for window icon, creating fallback")
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setPen(QColor(0, 120, 215))  # Windows blue
            painter.setBrush(QColor(0, 120, 215))
            painter.drawEllipse(8, 8, 48, 48)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "MS")
            painter.end()
            self.setWindowIcon(QIcon(pixmap))

        self.resize(600, 500)
        # Window should always show on first launch
    
    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Actions tab
        actions_tab = QWidget()
        actions_layout = QVBoxLayout()
        
        # Action list
        self.action_list = QListWidget()
        self.action_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.action_list.model().rowsMoved.connect(self.on_actions_reordered)
        actions_layout.addWidget(QLabel("Macro Actions:"))
        actions_layout.addWidget(self.action_list)
        
        # Action buttons
        action_buttons_layout = QHBoxLayout()
        self.add_action_btn = QPushButton("Add Action")
        self.add_action_btn.clicked.connect(self.on_add_action)
        self.edit_action_btn = QPushButton("Edit Action")
        self.edit_action_btn.clicked.connect(self.on_edit_action)
        self.remove_action_btn = QPushButton("Remove Action")
        self.remove_action_btn.clicked.connect(self.on_remove_action)
        self.test_action_btn = QPushButton("Test Action")
        self.test_action_btn.clicked.connect(self.on_test_action)
        
        action_buttons_layout.addWidget(self.add_action_btn)
        action_buttons_layout.addWidget(self.edit_action_btn)
        action_buttons_layout.addWidget(self.remove_action_btn)
        action_buttons_layout.addWidget(self.test_action_btn)
        actions_layout.addLayout(action_buttons_layout)
        
        # Test all button
        self.test_all_btn = QPushButton("Test All Actions")
        self.test_all_btn.clicked.connect(self.on_test_all_actions)
        actions_layout.addWidget(self.test_all_btn)
        
        actions_tab.setLayout(actions_layout)
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        
        # Idle time settings
        idle_group = QGroupBox("Idle Detection")
        idle_layout = QFormLayout()
        
        self.idle_spin = QSpinBox()
        self.idle_spin.setRange(10, 3600)
        self.idle_spin.setSingleStep(10)
        self.idle_spin.setSuffix(" seconds")
        self.idle_spin.valueChanged.connect(self.on_idle_time_changed)
        idle_layout.addRow("Run macro after idle time:", self.idle_spin)
        
        self.enabled_check = QCheckBox("Enable macro automation")
        self.enabled_check.stateChanged.connect(self.on_enabled_changed)
        idle_layout.addRow("", self.enabled_check)
        
        idle_group.setLayout(idle_layout)
        settings_layout.addWidget(idle_group)
        
        # Random delay settings
        delay_group = QGroupBox("Random Delay")
        delay_layout = QFormLayout()
        
        self.random_delay_check = QCheckBox("Add random delay between actions")
        self.random_delay_check.stateChanged.connect(self.on_random_delay_changed)
        delay_layout.addRow("", self.random_delay_check)
        
        delay_range_layout = QHBoxLayout()
        self.min_delay_spin = QSpinBox()
        self.min_delay_spin.setRange(0, 60)
        self.min_delay_spin.setSuffix(" seconds")
        self.min_delay_spin.valueChanged.connect(self.on_delay_range_changed)
        
        self.max_delay_spin = QSpinBox()
        self.max_delay_spin.setRange(1, 300)
        self.max_delay_spin.setSuffix(" seconds")
        self.max_delay_spin.valueChanged.connect(self.on_delay_range_changed)
        
        delay_range_layout.addWidget(QLabel("Min:"))
        delay_range_layout.addWidget(self.min_delay_spin)
        delay_range_layout.addWidget(QLabel("Max:"))
        delay_range_layout.addWidget(self.max_delay_spin)
        delay_layout.addRow("Delay range:", delay_range_layout)
        
        delay_group.setLayout(delay_layout)
        settings_layout.addWidget(delay_group)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout()

        self.startup_check = QCheckBox("Run on Windows startup")
        self.startup_check.stateChanged.connect(self.on_startup_changed)
        general_layout.addRow("", self.startup_check)

        # Add minimize to tray button
        minimize_btn = QPushButton("Minimize to Tray")
        minimize_btn.clicked.connect(self.hide)
        minimize_btn.setIcon(QIcon(resource_path("icon.ico")))
        general_layout.addRow("", minimize_btn)

        general_group.setLayout(general_layout)
        settings_layout.addWidget(general_group)
        
        # Status display
        status_group = QGroupBox("Status")
        status_layout = QFormLayout()
        
        self.status_label = QLabel("Idle time: 0 seconds")
        status_layout.addRow("", self.status_label)
        
        self.next_run_label = QLabel("Next run: Not scheduled")
        status_layout.addRow("", self.next_run_label)
        
        status_group.setLayout(status_layout)
        settings_layout.addWidget(status_group)
        
        # Add spacer
        settings_layout.addStretch()
        
        settings_tab.setLayout(settings_layout)
        
        # Add tabs
        tabs.addTab(actions_tab, "Actions")
        tabs.addTab(settings_tab, "Settings")
        
        main_layout.addWidget(tabs)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Update status timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
    
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)

        # Try to load the icon, with fallbacks
        icon_path = resource_path("icon.ico")
        if not os.path.exists(icon_path):
            # Try PNG version
            icon_path = resource_path("icon.png")

        if os.path.exists(icon_path):
            logger.info(f"Loading tray icon from: {icon_path}")
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Create a simple fallback icon if no icon file is found
            logger.warning("Icon files not found, creating fallback icon")
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setPen(QColor(0, 120, 215))  # Windows blue
            painter.setBrush(QColor(0, 120, 215))
            painter.drawEllipse(8, 8, 48, 48)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "MS")
            painter.end()
            self.tray_icon.setIcon(QIcon(pixmap))

        self.tray_icon.setToolTip(f"{APP_NAME} v{APP_VERSION}")
        
        # Create tray menu
        tray_menu = QMenu()
        
        self.toggle_action = QAction("Disable", self)
        self.toggle_action.triggered.connect(self.toggle_enabled)
        tray_menu.addAction(self.toggle_action)
        
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Update tray icon state
        self.update_tray_state()
    
    def setup_macro_engine(self):
        self.macro_thread = None
        self.macro_running = False
        self.last_idle_time = 0
        self.next_run_time = None
    
    def update_action_list(self):
        self.action_list.clear()
        for action in self.actions:
            item = ActionListWidgetItem(action)
            self.action_list.addItem(item)

        # Connect selection change signal if not already connected
        if not hasattr(self, '_selection_connected'):
            self.action_list.itemSelectionChanged.connect(self.update_controls_state)
            self._selection_connected = True

        # Select the first item if available
        if self.action_list.count() > 0:
            self.action_list.setCurrentRow(0)
    
    def update_controls_state(self):
        # Update button states based on selection
        has_selection = self.action_list.currentRow() >= 0
        self.edit_action_btn.setEnabled(has_selection)
        self.remove_action_btn.setEnabled(has_selection)
        self.test_action_btn.setEnabled(has_selection)
        
        # Update test all button
        self.test_all_btn.setEnabled(len(self.actions) > 0)
        
        # Update delay controls
        delay_enabled = self.random_delay_check.isChecked()
        self.min_delay_spin.setEnabled(delay_enabled)
        self.max_delay_spin.setEnabled(delay_enabled)
        
        # Update tray icon state
        self.update_tray_state()
    
    def update_tray_state(self):
        enabled = self.config_manager.is_enabled()
        self.toggle_action.setText("Disable" if enabled else "Enable")
        
        # Update tooltip with status
        status = "Enabled" if enabled else "Disabled"
        self.tray_icon.setToolTip(f"{APP_NAME} v{APP_VERSION} - {status}")
    
    def update_status(self):
        idle_time = get_idle_time()
        self.last_idle_time = idle_time
        self.status_label.setText(f"Idle time: {idle_time:.1f} seconds")
        
        if self.next_run_time is not None:
            time_left = max(0, self.next_run_time - idle_time)
            self.next_run_label.setText(f"Next run: in {time_left:.1f} seconds")
        else:
            self.next_run_label.setText("Next run: Not scheduled")
        
        # Check if we should start the macro
        if (self.config_manager.is_enabled() and 
            not self.macro_running and 
            idle_time >= self.config_manager.get_idle_time()):
            self.start_macro()
    
    def start_macro(self):
        if self.macro_running or not self.actions:
            return
        
        self.macro_running = True
        self.macro_thread = threading.Thread(target=self.run_macro)
        self.macro_thread.daemon = True
        self.macro_thread.start()
    
    def run_macro(self):
        try:
            logger.info("Starting macro execution")
            
            # Reset next run time
            self.next_run_time = None
            
            for action in self.actions:
                # Check if we should stop (if disabled or user activity detected)
                if not self.config_manager.is_enabled() or get_idle_time() < 1.0:
                    logger.info("Stopping macro execution: user activity detected or disabled")
                    break
                
                # Execute the action
                logger.info(f"Executing action: {action.name}")
                action.execute()
                
                # Add random delay if enabled
                if self.config_manager.get_random_delay():
                    min_delay, max_delay = self.config_manager.get_random_delay_range()
                    delay = random.uniform(min_delay, max_delay)
                    logger.info(f"Random delay: {delay:.1f} seconds")
                    time.sleep(delay)
            
            logger.info("Macro execution completed")
        except Exception as e:
            logger.error(f"Error in macro execution: {e}")
        finally:
            self.macro_running = False
            
            # Schedule next run if still idle and enabled
            if self.config_manager.is_enabled() and get_idle_time() >= 1.0:
                self.next_run_time = self.config_manager.get_idle_time()
    
    def on_add_action(self):
        try:
            dialog = ActionDialog(self)
            if dialog.exec():
                try:
                    action = dialog.action
                    if action:
                        # Verify the action can be executed without errors
                        logger.debug(f"Verifying new action: {action.name}")

                        self.actions.append(action)
                        self.update_action_list()
                        self.config_manager.set_actions(self.actions)
                        self.update_controls_state()
                    else:
                        logger.error("Action dialog returned but action is None")
                        QMessageBox.warning(self, "Error", "Failed to create action. Please try again.")
                except Exception as e:
                    logger.error(f"Error adding action: {e}", exc_info=True)
                    QMessageBox.critical(self, "Error", f"Failed to add action: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in on_add_action: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

    def on_edit_action(self):
        try:
            current_row = self.action_list.currentRow()
            if current_row >= 0:
                action = self.actions[current_row]
                dialog = ActionDialog(self, action)
                if dialog.exec():
                    try:
                        # Verify the action is valid
                        if action:
                            logger.debug(f"Updated action: {action.name}")
                            self.update_action_list()
                            self.config_manager.set_actions(self.actions)
                        else:
                            logger.error("Action dialog returned but action is None")
                            QMessageBox.warning(self, "Error", "Failed to update action. Please try again.")
                    except Exception as e:
                        logger.error(f"Error updating action: {e}", exc_info=True)
                        QMessageBox.critical(self, "Error", f"Failed to update action: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in on_edit_action: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
    
    def on_remove_action(self):
        current_row = self.action_list.currentRow()
        if current_row >= 0:
            del self.actions[current_row]
            self.update_action_list()
            self.config_manager.set_actions(self.actions)
            self.update_controls_state()
    
    def on_test_action(self):
        current_row = self.action_list.currentRow()
        if current_row >= 0:
            action = self.actions[current_row]
            
            # Hide window during test to avoid interference
            was_visible = self.isVisible()
            if was_visible:
                self.hide()
            
            # Wait a moment before executing
            QTimer.singleShot(500, lambda: self.execute_test_action(action, was_visible))
    
    def execute_test_action(self, action, restore_visibility):
        success = action.execute()
        
        # Show window again if it was visible
        if restore_visibility:
            QTimer.singleShot(500, self.show)
        
        # Show result
        if success:
            self.tray_icon.showMessage(
                "Action Test", 
                f"Action '{action.name}' executed successfully",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.tray_icon.showMessage(
                "Action Test", 
                f"Failed to execute action '{action.name}'",
                QSystemTrayIcon.MessageIcon.Warning,
                2000
            )
    
    def on_test_all_actions(self):
        if not self.actions:
            return
        
        # Hide window during test to avoid interference
        was_visible = self.isVisible()
        if was_visible:
            self.hide()
        
        # Wait a moment before executing
        QTimer.singleShot(500, lambda: self.execute_test_all_actions(was_visible))
    
    def execute_test_all_actions(self, restore_visibility):
        success_count = 0
        fail_count = 0
        
        for action in self.actions:
            if action.execute():
                success_count += 1
            else:
                fail_count += 1
            
            # Add a small delay between actions
            time.sleep(0.5)
        
        # Show window again if it was visible
        if restore_visibility:
            QTimer.singleShot(500, self.show)
        
        # Show result
        self.tray_icon.showMessage(
            "Actions Test", 
            f"Executed {success_count} actions successfully, {fail_count} failed",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def on_actions_reordered(self):
        # Update actions list after drag and drop reordering
        new_actions = []
        for i in range(self.action_list.count()):
            item = self.action_list.item(i)
            if isinstance(item, ActionListWidgetItem):
                new_actions.append(item.action)
        
        self.actions = new_actions
        self.config_manager.set_actions(self.actions)
    
    def on_idle_time_changed(self, value):
        self.config_manager.set_idle_time(value)
    
    def on_enabled_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.config_manager.set_enabled(enabled)
        self.update_controls_state()
    
    def on_startup_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.config_manager.set_run_on_startup(enabled)
    
    def on_random_delay_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.config_manager.set_random_delay(enabled)
        self.update_controls_state()
    
    def on_delay_range_changed(self):
        min_delay = self.min_delay_spin.value()
        max_delay = self.max_delay_spin.value()
        
        # Ensure max is always >= min
        if max_delay < min_delay:
            self.max_delay_spin.setValue(min_delay)
            max_delay = min_delay
        
        self.config_manager.set_random_delay_range(min_delay, max_delay)
    
    def toggle_enabled(self):
        enabled = not self.config_manager.is_enabled()
        self.config_manager.set_enabled(enabled)
        self.enabled_check.setChecked(enabled)
        self.update_controls_state()
        
        # Show notification
        status = "enabled" if enabled else "disabled"
        self.tray_icon.showMessage(
            APP_NAME,
            f"Macro automation {status}",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def closeEvent(self, event):
        """Handle window close event"""
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()

        # Show notification first time
        if not hasattr(self, '_shown_minimize_notice'):
            self.tray_icon.showMessage(
                APP_NAME,
                f"{APP_NAME} is still running in the system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            self._shown_minimize_notice = True

    def quit_application(self):
        reply = QMessageBox.question(
            self,
            "Quit Confirmation",
            f"Are you sure you want to quit {APP_NAME}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
    
    def closeEvent(self, event):
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        
        # Show notification first time
        if not hasattr(self, '_shown_minimize_notice'):
            self.tray_icon.showMessage(
                APP_NAME,
                f"{APP_NAME} is still running in the system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            self._shown_minimize_notice = True


def main():
    # Ensure single instance
    mutex = ensure_single_instance()
    if mutex is None:
        sys.exit(1)
    
    # Create application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Don't quit when window is closed
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start application event loop
    exit_code = app.exec()
    
    # Release mutex on exit
    ctypes.windll.kernel32.ReleaseMutex(mutex)
    ctypes.windll.kernel32.CloseHandle(mutex)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()