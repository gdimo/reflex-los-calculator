# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---
## [0.7] - 2025-01-08
### Added
- Now the los script supports rxagn1 calculations

## [0.6] – 2025-01-07
### Added
- Full support for hollow-cone (polar wind) geometry, consistent with the RXToPo / RXagn1 grid-generation pipeline
- New user input for hollow-cone column density `log10(NH_cone)` (interactive and CLI via `--cone-nh`)
- Automatic computation of hollow-cone geometry parameters from covering factor (CF) and sublimation radius:
  - Bottom and top heights of the cone
  - Inner and outer radial boundaries at the bottom and top surfaces
  - Volumetric cone density derived from column density and geometric path length
- Hollow-cone geometry passed to RefleX via new substitution variables:
  - `%HCONEDENS`
  - `%HCONEBOT`, `%HCONETOP`
  - `%HCONERBOUT`, `%HCONERTOUT`
  - `%HCONERBIN`, `%HCONERTIN`
- Automatic computation and exposure of hollow-cone angular geometry:
  - Inner cone angle θ_in (degrees)
  - Outer cone angle θ_out (degrees)

### Changed
- RefleX execution command updated to include hollow-cone density and geometry parameters
- Runtime logging now includes hollow-cone angular boundaries (θ_in, θ_out) for full geometry traceability
- Output summary file (`output.txt`) expanded to include:
  - Hollow-cone NH
  - Hollow-cone density
  - Hollow-cone radial geometry
  - Hollow-cone inner and outer angles
- Internal geometry calculations reorganized into dedicated physics helper functions for maintainability and future extension

### Notes
- Hollow-cone implementation exactly reproduces the geometry and density calculations used in the original RXToPo / RXagn1 grid-generation scripts
- This version completes the physical geometry model for LOS calculations, including both torus and polar components


## [0.5] – 2025-11-27
### Added
- Support for torus covering factor (CF) as a new input parameter (interactive + CLI via `--covfac`)
- Automatic computation of torus inner and outer radii:
  - `%RTORUSIN` = Rin
  - `%RTORUSDIST` = Rout
  using the formula from the RXToPo grid builder
- Sublimation radius constant added (3.1072024e17 cm)
- Summary file now includes CF, sublimation radius, Rin, and Rout
- Updated README and USAGE documentation with CF usage instructions

### Changed
- RefleX command now includes `%RTORUSIN` and `%RTORUSDIST`
- `.par` file requirements updated to include new geometry variables

### Notes
- This update brings LOS mode geometry into full consistency with the RXToPo grid-generation pipeline.

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
