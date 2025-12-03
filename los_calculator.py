#!/usr/bin/env python3
import os
import subprocess
import math
from datetime import datetime
import shutil

# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')


def get_float(prompt):
    """Prompt user for a numeric (float) input."""
    while True:
        val = input(prompt)
        try:
            return float(val)
        except ValueError:
            print("❌ ERROR: Value must be numeric.")


def get_choice(prompt, options):
    """Prompt user to enter one of the allowed string options."""
    while True:
        val = input(prompt).strip()
        if val in options:
            return val
        print(f"❌ ERROR: Enter one of: {', '.join(options)}")


# ---------------------------------------------------------------------
# Banner + Requirements
# ---------------------------------------------------------------------

def welcome():
    clear_screen()
    print("==============================================================")
    print("        Welcome to the RefleX Line-of-Sight NH Utility")
    print("==============================================================")
    print("\nThis script runs LOS NH simulations using RefleX (v3).\n")
    print("Requirements:")
    print("  • RefleX v3 executable named 'reflex3' in the same directory")
    print("  • Parameter files must contain: %COSMIN, %COSMAX, %ANGLE, %TORUSNH")
    print("  • COLDENS must appear as:  COLDENS 1e%TORUSNH")
    print("\n--------------------------------------------------------------")


# ---------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------

def main():

    welcome()

    # ------------------------------------------
    # Check for reflex3 executable
    # ------------------------------------------
    if not os.path.isfile("./reflex3") or not os.access("./reflex3", os.X_OK):
        print("❌ ERROR: Missing executable './reflex3'")
        return

    print("RefleX executable found.\n")

    # ------------------------------------------
    # Model Selection
    # ------------------------------------------
    print("Which model do you want to use?")
    print("  [1] RXToPo  (rxtopo_los.par)")
    print("  [2] RXagn1  (rxagn1_los.par)")

    choice = get_choice("Enter 1 or 2: ", ["1", "2"])

    if choice == "1":
        model_file = "rxtopo_los.par"
        model_name = "RXToPo"
    else:
        model_file = "rxagn1_los.par"
        model_name = "RXagn1"

    print(f"\nSelected model: {model_name}")

    if not os.path.isfile(model_file):
        print(f"❌ ERROR: Parameter file not found: {model_file}")
        return

    # ------------------------------------------
    # Observing angle
    # ------------------------------------------
    obs_angle = get_float("\nEnter observing angle in degrees (e.g. 79): ")

    theta_min = obs_angle - 0.5
    theta_max = obs_angle + 0.5

    COSMIN = math.cos(math.radians(theta_min))
    COSMAX = math.cos(math.radians(theta_max))

    print("\nComputed DIR_Z range:")
    print(f"   theta_min = {theta_min}° → cos = {COSMIN}")
    print(f"   theta_max = {theta_max}° → cos = {COSMAX}")

    # ------------------------------------------
    # Torus NH (log10)
    # ------------------------------------------
    torus_nh = get_float("\nEnter Torus equatorial NH (log10, e.g. 24.4): ")
    print(f"Using COLDENS = 1e{torus_nh}\n")

    # ------------------------------------------
    # Output directory
    # ------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"outputs/{model_name}_{obs_angle}deg_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    log_file = f"{output_dir}/run_{model_name}_{obs_angle}deg_{timestamp}.log"

    print(f"Output directory: {output_dir}")
    print(f"Log file:         {log_file}\n")

    input("Press ENTER to start simulation, or Ctrl+C to cancel.")
    print("\nRunning RefleX...\n")

    # ------------------------------------------
    # Build RefleX command
    # ------------------------------------------
    reflex_cmd = [
        "./reflex3",
        f"%COSMIN={COSMIN}",
        f"%COSMAX={COSMAX}",
        f"%ANGLE={obs_angle}",
        f"%TORUSNH={torus_nh}",
        model_file
    ]

    # ------------------------------------------
    # Run with full logging
    # ------------------------------------------
    with open(log_file, "w") as logf:
        logf.write("=== RefleX run started ===\n")
        logf.write("Command:\n")
        logf.write(" ".join(reflex_cmd) + "\n\n")

        try:
            subprocess.run(reflex_cmd, stdout=logf, stderr=logf, check=False)
        except Exception as e:
            logf.write(f"\nERROR running RefleX: {e}\n")

        logf.write("\n=== RefleX run finished ===\n")

    # ------------------------------------------
    # Locate output
    # ------------------------------------------
    outfile = f"NHdeg{obs_angle}.txt"
    moved_outfile = f"{output_dir}/{outfile}"

    if not os.path.isfile(outfile):
        print("⚠️ Simulation finished but no NH output found.")
        print(f"Check log: {log_file}")
        return

    shutil.move(outfile, moved_outfile)
    print(f"Simulation successful.\nNH file saved to: {moved_outfile}")

    # ------------------------------------------
    # Analyze histogram
    # ------------------------------------------
    print("\nAnalyzing histogram...")

    peak_mid = None
    max_count = -1

    with open(moved_outfile) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 3:
                continue
            nh1, nh2, count = map(float, parts)
            if count > max_count:
                max_count = count
                peak_mid = (nh1 + nh2) / 2.0

    if max_count <= 0:
        print("⚠️ Histogram has no non-zero bins.")
        peak_log = "undefined"
    else:
        peak_log = f"{math.log10(peak_mid):.4f}"
        print(f"Peak NH midpoint = {peak_mid}  (debug)")
        print(f"Peak log10(NH)   = {peak_log}")

    # ------------------------------------------
    # Ask user whether to keep output directory
    # ------------------------------------------
    keep = get_choice("\nDo you want to keep the output files? (1 = yes, 0 = no): ", ["1", "0"])

    if keep == "1":
        summary_file = f"{output_dir}/output.txt"
        with open(summary_file, "w") as f:
            f.write("RefleX LOS NH Simulation Summary\n")
            f.write("================================\n\n")
            f.write(f"Model used: {model_name}\n")
            f.write(f"Parameter file: {model_file}\n\n")
            f.write(f"Observing angle: {obs_angle} degrees\n")
            f.write(f"Torus equatorial NH (log10): {torus_nh}\n\n")
            f.write("DIR_Z boundaries:\n")
            f.write(f"   theta_min = {theta_min}° -> cos = {COSMIN}\n")
            f.write(f"   theta_max = {theta_max}° -> cos = {COSMAX}\n\n")
            f.write(f"LOS NH (log10): {peak_log}\n\n")
            f.write("Output directory:\n")
            f.write(f"   {output_dir}\n\n")
            f.write("Log file:\n")
            f.write(f"   {log_file}\n\n")
            f.write("----------------------------------------------\n")
            f.write("End of summary\n")

        print(f"Summary saved in {summary_file}")

    else:
        print("Deleting all output files...")
        shutil.rmtree(output_dir)
        print("Output directory deleted. LOS NH was NOT saved.")

    print("\n==============================================================")
    print("Done.")


# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()
