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
## Geometry Model

This tool implements a physically consistent AGN circumnuclear geometry
composed of two main components:

1. **Equatorial torus**
2. **Polar hollow cone (wind/outflow)**

Both components are implemented following the exact prescriptions used in
the RXToPo / RXagn1 grid-generation pipeline, ensuring full consistency
between LOS calculations and spectral model grids.

### Torus Geometry

The torus geometry is controlled by two user parameters:

- **Torus equatorial column density** `log10(NH)`
- **Covering factor (CF)**

From the covering factor and a fixed sublimation radius
$( R_{\mathrm{sub}} = 3.1072 \times 10^{17} \,\mathrm{cm} )$,
the torus radii are computed as:

$R_{\mathrm{in}} = \frac{\mathrm{CF}}{1 - \mathrm{CF}} R_{\mathrm{sub}}$

$R_{\mathrm{out}} = R_{\mathrm{sub}} + R_{\mathrm{in}}$

These values are automatically passed to RefleX via:

- `%RTORUSIN` — inner torus radius (cm)
- `%RTORUSDIST` — outer torus radius (cm)

The torus column density is passed as:

### Hollow Cone (Polar Wind) Geometry

The polar component is modeled as a **hollow cone**, representing an
ionized or molecular outflow aligned with the polar axis.

The hollow cone is defined by:

- A **column density** `log10(NH_cone)`
- A **covering factor–dependent opening angle**
- A fixed **height** of 40 pc
- A fixed **angular thickness** of 10°

The cone geometry is derived from the torus covering factor CF:

$\phi = \arcsin(\mathrm{CF})$

$\theta_{\mathrm{out}} = 90^\circ - (\phi + 1^\circ)$

$\theta_{\mathrm{in}} = \theta_{\mathrm{out}} - 10^\circ $

From these angles, the inner and outer radial boundaries of the cone
are computed at both the bottom (sublimation radius) and the top
(40 pc).

The cone density is derived self-consistently from the cone column density
and the physical path length through the cone.

---
## Requirements

- **RefleX v3 executable** (must be named `reflex3`)
- Shell environment (macOS or Linux)
- Python 3 (for computing log10 values)
Parameter files with RefleX variable placeholders:
  - %COSMIN
  - %COSMAX
  - %ANGLE
  - %TORUSNH
  - %RTORUSIN
  - %RTORUSDIST
  - %HCONEDENS
  - %HCONEBOT
  - %HCONETOP
  - %HCONERBIN
  - %HCONERTIN
  - %HCONERBOUT
  - %HCONERTOUT

Example expected line in your `.par` file:

## Output

- `NHdegXX.txt` — LOS NH histogram
- `output.txt` — simulation summary
- `run_*.log` — RefleX execution log

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
    --cone-nh 23.0 \
    --keep 1
```
- This way the procedure can be scripted for multiple sources.

### Hybrid mode

- It is a combination of the two modes. You can automate some of the parameters and you will be promted to supply the rest.
- For example:
`python3 los_calculator.py --model rxagn1 --angle 75`  