# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---
## [0.4] – 2025-11-26
### Added
- Complete Python version of the LOS NH calculator (`los_calculator.py`)
- Modular function-based structure for angle math, histogram parsing, summary writing, and RefleX execution
- Hybrid input system: supports both interactive prompts and argument-based execution
- Full command-line interface using argparse (`--model`, `--angle`, `--nh`, `--keep`, `--delta`)
- Fully automatic mode for batch scripting without user interaction
- Output directory, summary file, and histogram handling reproduced exactly from the Bash script
### Changed
- Internal structure reorganized for extensibility (future geometric parameters, batch tools, GUI)
### Notes
- Python version mirrors the Bash version exactly but is more robust, maintainable, and scriptable.


## [0.3.1] – 2025-11-27
### Changed
- Rewrote angle logic to use ±0.5° boundaries 

## [0.3] – 2025-11-25
### Added
- User option to save or delete output files after simulation
- Summary report (`output.txt`) generated when output is saved
- Log files and simulation outputs now stored under the main output directory
- Histogram midpoint and log10 NH extraction
- Completed simulation workflow with model selection, angle input, torus NH input, and DIR_Z computation

### Changed
- Moved log directory inside the main output directory for easier cleanup
- Improved structure for reproducibility and GitHub readiness

---

## [0.2] – 2025-11-24
### Added
- Support for `%TORUSNH` variable substitution
- Simplified COLDENS handling using `1e%TORUSNH`
- Full logging block with start/end timestamps
- Output folder creation with timestamps

### Changed
- Rewrote angle logic to use ±1° boundaries instead of ±0.5°
- Cleaned script logic and error handling

---

## [0.1] – 2025-11-23
### Added
- Initial version of `los_calculator.sh`
- Model selection menu (RXToPo / RXagn1)
- Angle input and basic DIR_Z computation
- Basic RefleX validation and execution
- Initial parameter substitution support

---

## [Unreleased]
- Future expansions: multi-angle batch mode, cone NH computation, spectrum extraction, GUI wrapper, and automated plotting.
