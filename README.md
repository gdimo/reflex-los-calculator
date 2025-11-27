# RefleX Line-of-Sight NH Calculator

This repository contains a command-line utility for running 
**LOS (Line-of-Sight) column density calculations** using the 
**RefleX v3** simulation code (Paltani & Ricci 2017).

---

## Purpose

The goal of this tool is to provide a **simple and user-friendly front-end**
to the RefleX simulation framework, allowing astronomers to:

- Select between custom AGN geometry models (RXToPo and RXagn1)
- Specify an observing angle (in degrees)
- Provide a torus equatorial column density (in log10 units)
- Automatically compute the correct DIR_Z angular boundaries
- Run RefleX with the chosen parameters
- Extract the LOS NH from the generated histogram
- Optionally save or delete all simulation output
- Automatically generate a summary report

This script hides the internal complexity of RefleX and provides a 
clean interface suited for scientific analysis pipelines.

---

## Requirements

- **RefleX v3 executable** (must be named `reflex3`)
- Shell environment (macOS or Linux)
- Python 3 (for computing log10 values)
- Parameter files with RefleX variable placeholders:
  - `%COSMIN`
  - `%COSMAX`
  - `%ANGLE`
  - `%TORUSNH`

Example expected line in your `.par` file:

