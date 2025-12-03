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

---


## How to

A short description of how to properly use the script. There are three modes; _interactive_, _automatic_ and _hybrid_.

### Interactive mode

- Simply execute  
`python los_calculator.py`  
and follow the instructions in the screen
- You will be prompted to select the model, and its parameters as well as whether you want to keep the output in separate files.
- You should see:  
```
Which model do you want to use?
  [1] RXToPo
  [2] RXagn1
Enter 1 or 2:
Enter observing angle:
Enter torus NH (log10):
.
.
.
Do you want to keep the output files? (1=yes, 0=no)
```

### Automatic mode
- Execute the script with command-line arguments (an example):
```
python3 los_calculator.py \
    --model rxtopo \
    --angle 79 \
    --nh 24.4 \
    --covfac 0.5 \
    --keep 1
```
- This way the procedure can be scripted for multiple sources.

### Hybrid mode

- It is a combination of the two modes. You can automate some of the parameters and you will be promted to supply the rest.
- For example:
`python3 los_calculator.py --model rxagn1 --angle 75
`  