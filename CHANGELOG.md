# Changelog

All notable changes to MagicScript will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-27

### Added
- Initial release of MagicScript
- Mouse movement actions (specific coordinates, random in range, fully random, relative to current position)
- Mouse click actions (left, right, middle buttons with customizable click count)
- Mouse scroll actions (fixed or random amounts)
- Keyboard actions (key press and key combinations)
- Wait/delay actions
- Idle detection with configurable threshold
- Random delays between actions
- System tray integration
- Action testing capabilities
- Run on Windows startup option
- Comprehensive error handling and logging
- Drag-and-drop action reordering

## [1.1.0] - 2025-03-27

### Added
- New "Random Range from Current Position" mouse movement option
- Enhanced error handling and logging
- Improved configuration file handling
- Better UI feedback for validation errors

### Fixed
- Fixed issue with configuration saving
- Resolved UI crashes when editing certain action types
- Improved error recovery for invalid actions
- Fixed label updating in the action dialog

## [Unreleased]

### Planned Features
- Macro recording capability
- Multiple macro profiles
- Scheduled macros (time-based rather than idle-based)
- Export/import macro configurations
- Hotkey support for manual macro triggering
- More advanced mouse movement patterns
- Screen region detection for conditional actions