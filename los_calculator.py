#!/usr/bin/env python3
"""
RefleX Line-of-Sight NH Utility (Python version)

- Supports interactive mode (no arguments)
- Supports argument-based mode for scripting / batches
- Mirrors functionality of the original Bash script
- Now includes covering factor -> torus radii (Rin, Rout) via %RTORUSIN, %RTORUSDIST
"""

import os
import math
import shutil
import subprocess
from datetime import datetime
import argparse

# Sublimation radius constant (from original grid script)
RSUBLIMATION = 3.1072024e17  # cm


# -----------------------------------------------------------
# UI + Input Helpers
# -----------------------------------------------------------

def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def ask_float(prompt):
    """Prompt user for a numeric (float) input."""
    while True:
        val = input(prompt).strip()
        try:
            return float(val)
        except ValueError:
            print("❌ ERROR: Value must be numeric.")


def ask_choice(prompt, choices):
    """Prompt user to enter one of the allowed string options."""
    while True:
        val = input(prompt).strip()
        if val in choices:
            return val
        print(f"❌ ERROR: Enter one of: {', '.join(choices)}")


def print_banner():
    print("==============================================================")
    print("        Welcome to the RefleX Line-of-Sight NH Utility")
    print("==============================================================")
    print("")
    print("This script runs LOS NH simulations using RefleX (v3).")
    print("")
    print("Requirements:")
    print("  • RefleX v3 executable named 'reflex3' in the same directory")
    print("  • Parameter files must contain: %COSMIN, %COSMAX, %ANGLE, %TORUSNH")
    print("  • Torus radii must use: %RTORUSIN, %RTORUSDIST")
    print("  • COLDENS must appear as:  COLDENS 1e%TORUSNH")
    print("")
    print("--------------------------------------------------------------")


# -----------------------------------------------------------
# Math + Physics Helpers
# -----------------------------------------------------------

def compute_angle_cosines(obs_angle, delta=0.5):
    """
    Given observing angle (deg) and half-width delta (deg),
    return (theta_min, theta_max, COSMIN, COSMAX).
    """
    theta_min = obs_angle - delta
    theta_max = obs_angle + delta
    cosmin = math.cos(math.radians(theta_min))
    cosmax = math.cos(math.radians(theta_max))
    return theta_min, theta_max, cosmin, cosmax


def compute_torus_radii(r_sub, covfac=0.6):
    """
    From the original grid script:
        r_in = (cf / (1 - cf)) * rsub
        R_distance = rsub + r_in
    """
    r_in = (covfac / (1.0 - covfac)) * r_sub
    r_out = r_sub + r_in
    return r_in, r_out


# -----------------------------------------------------------
# Histogram Analysis
# -----------------------------------------------------------

def analyze_histogram(histogram_path):
    """
    Analyze NH histogram file with format:
      NH_low   NH_high   count
    Return (peak_mid, peak_log10) or (None, 'undefined') if empty.
    """
    max_count = -1.0
    peak_mid = None

    with open(histogram_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 3:
                continue
            try:
                nh1, nh2, count = map(float, parts)
            except ValueError:
                continue
            if count > max_count:
                max_count = count
                peak_mid = (nh1 + nh2) / 2.0

    if max_count <= 0 or peak_mid is None:
        return None, "undefined"

    peak_log = math.log10(peak_mid)
    return peak_mid, f"{peak_log:.4f}"


# -----------------------------------------------------------
# RefleX Execution
# -----------------------------------------------------------

def run_reflex(model_file, cosmin, cosmax, angle_str, torus_nh,
               r_in, r_out, log_file):
    """
    Execute RefleX with the given parameters and log stdout/stderr.
    Now also passes %RTORUSIN and %RTORUSDIST.
    """
    cmd = [
        "./reflex3",
        f"%COSMIN={cosmin}",
        f"%COSMAX={cosmax}",
        f"%ANGLE={angle_str}",
        f"%TORUSNH={torus_nh}",
        f"%RTORUSIN={r_in}",
        f"%RTORUSDIST={r_out}",
        model_file,
    ]

    with open(log_file, "w") as log:
        log.write("=== RefleX run started ===\n")
        log.write("Command:\n")
        log.write(" ".join(cmd) + "\n\n")

        subprocess.run(cmd, stdout=log, stderr=log, check=False)

        log.write("\n=== RefleX run finished ===\n")


# -----------------------------------------------------------
# Summary and File Handling
# -----------------------------------------------------------

def write_summary(output_dir, model_name, model_file,
                  obs_angle, torus_nh, covfac,
                  theta_min, theta_max, cosmin, cosmax,
                  r_in, r_out,
                  peak_log, log_file):
    """
    Write a short summary file (output.txt) in the output directory.
    """
    summary_file = os.path.join(output_dir, "output.txt")
    with open(summary_file, "w") as f:
        f.write("RefleX LOS NH Simulation Summary\n")
        f.write("================================\n\n")
        f.write(f"Model used: {model_name}\n")
        f.write(f"Parameter file: {model_file}\n\n")
        f.write(f"Observing angle: {obs_angle} degrees\n")
        f.write(f"Torus equatorial NH (log10): {torus_nh}\n")
        f.write(f"Torus covering factor (CF): {covfac}\n")
        f.write(f"Sublimation radius (cm): {RSUBLIMATION:.4e}\n")
        f.write(f"Torus Rin (cm): {r_in:.4e}\n")
        f.write(f"Torus Rout (cm): {r_out:.4e}\n\n")
        f.write("DIR_Z boundaries:\n")
        f.write(f"   theta_min = {theta_min}°  -> cos = {cosmin}\n")
        f.write(f"   theta_max = {theta_max}°  -> cos = {cosmax}\n\n")
        f.write(f"LOS NH (log10): {peak_log}\n\n")
        f.write("Output directory:\n")
        f.write(f"   {output_dir}\n\n")
        f.write("Log file:\n")
        f.write(f"   {log_file}\n\n")
        f.write("----------------------------------------------\n")
        f.write("End of summary\n")

    print(f"Summary saved in {summary_file}")


# -----------------------------------------------------------
# Argument Parsing
# -----------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="RefleX LOS NH utility (interactive + CLI mode)"
    )
    parser.add_argument(
        "--model",
        choices=["rxtopo", "rxagn1"],
        help="Model to use: rxtopo or rxagn1"
    )
    parser.add_argument(
        "--angle",
        type=float,
        help="Observing angle in degrees (e.g. 79)"
    )
    parser.add_argument(
        "--nh",
        type=float,
        help="Torus equatorial NH (log10, e.g. 24.4)"
    )
    parser.add_argument(
        "--covfac",
        type=float,
        help="Torus covering factor (0 < CF < 1, e.g. 0.5)"
    )
    parser.add_argument(
        "--keep",
        type=int,
        choices=[0, 1],
        help="Keep output files? 1 = yes, 0 = no"
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=0.5,
        help="Half-width of angle bin in degrees (default: 0.5)"
    )
    return parser.parse_args()


# -----------------------------------------------------------
# Main Orchestration
# -----------------------------------------------------------

def main():
    clear_screen()
    print_banner()

    args = parse_arguments()

    # --- Check for executable ---
    if not (os.path.isfile("./reflex3") and os.access("./reflex3", os.X_OK)):
        print("❌ ERROR: Missing executable './reflex3'")
        return

    print("RefleX executable found.\n")

    # --- Model selection ---
    if args.model is None:
        print("Which model do you want to use?")
        print("  [1] RXToPo  (rxtopo_los.par)")
        print("  [2] RXagn1  (rxagn1_los.par)")
        choice = ask_choice("Enter 1 or 2: ", ["1", "2"])
        if choice == "1":
            model_file = "rxtopo_los.par"
            model_name = "RXToPo"
        else:
            model_file = "rxagn1_los.par"
            model_name = "RXagn1"
    else:
        if args.model == "rxtopo":
            model_file = "rxtopo_los.par"
            model_name = "RXToPo"
        else:
            model_file = "rxagn1_los.par"
            model_name = "RXagn1"

    print(f"\nSelected model: {model_name}")

    if not os.path.isfile(model_file):
        print(f"❌ ERROR: Parameter file not found: {model_file}")
        return

    # --- Observing angle ---
    if args.angle is None:
        obs_angle = ask_float("\nEnter observing angle in degrees (e.g. 79): ")
    else:
        obs_angle = float(args.angle)

    # Angle string for passing to RefleX and file names
    if float(obs_angle).is_integer():
        angle_str = str(int(obs_angle))
    else:
        angle_str = str(obs_angle)

    theta_min, theta_max, cosmin, cosmax = compute_angle_cosines(
        obs_angle,
        delta=args.delta
    )

    print("\nComputed DIR_Z range:")
    print(f"   theta_min = {theta_min}° → cos = {cosmin}")
    print(f"   theta_max = {theta_max}° → cos = {cosmax}")

    # --- Torus NH (log10) ---
    if args.nh is None:
        torus_nh = ask_float("\nEnter Torus equatorial NH (log10, e.g. 24.4): ")
    else:
        torus_nh = float(args.nh)

    print(f"Using COLDENS = 1e{torus_nh}\n")

    # --- Covering factor CF ---
    if args.covfac is None:
        while True:
            covfac = ask_float("Enter torus covering factor CF (0.1 < CF < 0.9): ")
            if 0.0 < covfac < 1.0:
                break
            print("❌ ERROR: CF must be between 0.1 and 0.9 (exclusive).")
    else:
        covfac = float(args.covfac)
        if not (0.0 < covfac < 1.0):
            print("❌ ERROR: CF must be between 0.1 and 0.9 (exclusive).")
            return

    r_in, r_out = compute_torus_radii(RSUBLIMATION, covfac)

    print(f"\nUsing torus geometry from CF:")
    print(f"   CF = {covfac}")
    print(f"   Rin  = {r_in:.4e} cm")
    print(f"   Rout = {r_out:.4e} cm\n")

    # --- Prepare output directory ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(
        "outputs",
        f"{model_name}_{angle_str}deg_{timestamp}"
    )
    os.makedirs(output_dir, exist_ok=True)

    log_file = os.path.join(
        output_dir,
        f"run_{model_name}_{angle_str}deg_{timestamp}.log"
    )

    print(f"Output directory: {output_dir}")
    print(f"Log file:         {log_file}\n")

    # Pause only if some inputs came from interaction
    if (args.model is None or
        args.angle is None or
        args.nh is None or
        args.covfac is None or
        args.keep is None):
        input("Press ENTER to start simulation, or Ctrl+C to cancel.")
        print("")

    print("Running RefleX...\n")

    # --- Run RefleX ---
    run_reflex(
        model_file=model_file,
        cosmin=cosmin,
        cosmax=cosmax,
        angle_str=angle_str,
        torus_nh=torus_nh,
        r_in=r_in,
        r_out=r_out,
        log_file=log_file,
    )

    # --- Locate NH output ---
    outfile_name = f"NHdeg{angle_str}.txt"
    outfile_path = outfile_name
    moved_outfile = os.path.join(output_dir, outfile_name)

    if not os.path.isfile(outfile_path):
        print("⚠️ Simulation finished but no NH output found.")
        print(f"Check log: {log_file}")
        return

    shutil.move(outfile_path, moved_outfile)
    print(f"Simulation successful.")
    print(f"NH file saved to: {moved_outfile}")

    # --- Analyze histogram ---
    print("\nAnalyzing histogram...")

    peak_mid, peak_log = analyze_histogram(moved_outfile)

    if peak_mid is None:
        print("⚠️ Histogram has no non-zero bins.")
    else:
        print(f"Peak NH midpoint = {peak_mid}  (Ignore/Debug use only)")
        print(f"Peak log10(NH)   = {peak_log}")

    # --- Keep or delete output directory ---
    if args.keep is None:
        keep_str = ask_choice(
            "\nDo you want to keep the output files? (1 = yes, 0 = no): ",
            ["1", "0"]
        )
        keep = int(keep_str)
    else:
        keep = int(args.keep)

    if keep == 1:
        write_summary(
            output_dir=output_dir,
            model_name=model_name,
            model_file=model_file,
            obs_angle=obs_angle,
            torus_nh=torus_nh,
            covfac=covfac,
            theta_min=theta_min,
            theta_max=theta_max,
            cosmin=cosmin,
            cosmax=cosmax,
            r_in=r_in,
            r_out=r_out,
            peak_log=peak_log,
            log_file=log_file,
        )
    else:
        print("\nDeleting all output files...")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        print("Output directory deleted. LOS NH was NOT saved.")

    print("\n==============================================================")
    print("Done.")


# -----------------------------------------------------------

if __name__ == "__main__":
    main()
