#!/bin/bash

clear

echo "=============================================================="
echo "        Welcome to the RefleX Line-of-Sight NH Utility"
echo "=============================================================="
echo ""
echo "This script runs LOS NH simulations using RefleX (v3)."
echo ""
echo "Requirements:"
echo "  • RefleX v3 executable named 'reflex3' in the same directory"
echo "  • Parameter files must contain: %COSMIN, %COSMAX, %ANGLE, %TORUSNH"
echo "  • COLDENS must appear as:  COLDENS 1e%TORUSNH"
echo ""
echo "--------------------------------------------------------------"

# --- Check for executable ---
if [[ ! -x "./reflex3" ]]; then
    echo "❌ ERROR: Missing executable './reflex3'"
    exit 1
fi

echo "RefleX executable found."
echo ""

# --- Model selection ---
echo "Which model do you want to use?"
echo "  [1] RXToPo  (rxtopo_los.par)"
echo "  [2] RXagn1  (rxagn1_los.par)"
read -p "Enter 1 or 2: " choice

if [[ "$choice" == "1" ]]; then
    model_file="rxtopo_los.par"
    model_name="RXToPo"
elif [[ "$choice" == "2" ]]; then
    model_file="rxagn1_los.par"
    model_name="RXagn1"
else
    echo "❌ Invalid selection."
    exit 1
fi

echo ""
echo "Selected model: $model_name"

if [[ ! -f "$model_file" ]]; then
    echo "❌ ERROR: Parameter file not found: $model_file"
    exit 1
fi

# --- Angle input ---
echo ""
read -p "Enter observing angle in degrees (e.g. 79): " obs_angle

if ! [[ "$obs_angle" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo "❌ ERROR: Angle must be numeric."
    exit 1
fi

theta_min=$(echo "$obs_angle - 1" | bc -l)
theta_max=$(echo "$obs_angle + 1" | bc -l)

pi="3.141592653589793"
COSMIN=$(echo "c($theta_min*$pi/180)" | bc -l)
COSMAX=$(echo "c($theta_max*$pi/180)" | bc -l)

echo ""
echo "Computed DIR_Z range:"
echo "   theta_min = $theta_min° → cos = $COSMIN"
echo "   theta_max = $theta_max° → cos = $COSMAX"

# --- Torus NH input (log10) ---
echo ""
read -p "Enter Torus equatorial NH (log10, e.g. 24.4): " torus_nh

if ! [[ "$torus_nh" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo "❌ ERROR: NH must be numeric."
    exit 1
fi

echo "Using COLDENS = 1e$torus_nh"
echo ""

# --- Prepare output parent directory ---
timestamp=$(date +"%Y%m%d_%H%M%S")
output_dir="outputs/${model_name}_${obs_angle}deg_${timestamp}"

mkdir -p "$output_dir"

log_file="${output_dir}/run_${model_name}_${obs_angle}deg_${timestamp}.log"

echo "Output directory: $output_dir"
echo "Log file: $log_file"
echo ""

read -p "Press ENTER to start simulation, or Ctrl+C to cancel."
echo ""
echo "Running RefleX..."
echo ""

# --- Full logging ---
{
    echo "=== RefleX run started at $(date) ==="
    echo "Command:"
    echo "./reflex3 %COSMIN=$COSMIN %COSMAX=$COSMAX %ANGLE=$obs_angle %TORUSNH=$torus_nh $model_file"
    echo ""

    ./reflex3 \
        %COSMIN=$COSMIN \
        %COSMAX=$COSMAX \
        %ANGLE=$obs_angle \
        %TORUSNH=$torus_nh \
        "$model_file"

    echo ""
    echo "=== RefleX run finished at $(date) ==="
} &> "$log_file"


# --- Locate NH output ---
outfile="NHdeg${obs_angle}.txt"

if [[ -f "$outfile" ]]; then
    mv "$outfile" "$output_dir/"
    echo "Simulation successful."
    echo "NH file saved to: $output_dir/$outfile"
else
    echo "⚠️ Simulation finished but no NH output found."
    echo "Check log: $log_file"
    exit 1
fi


# --- Analyze histogram ---
echo ""
echo "Analyzing histogram..."

peak_mid=$(awk '
{
    nh1=$1; nh2=$2; c=$3;
    if (c > max) {
        max = c;
        mid = (nh1 + nh2) / 2.0;
    }
}
END { if (max > 0) print mid; else print "NONE"; }
' "$output_dir/$outfile")

if [[ "$peak_mid" == "NONE" ]]; then
    echo "⚠️ Histogram has no non-zero bins."
    peak_log="undefined"
else
    peak_log=$(python3 - <<EOF
import math
print("{:.4f}".format(math.log10(float("$peak_mid"))))
EOF
)
    echo "Peak NH midpoint = $peak_mid" "Ignore/Debug use only"
    echo "Peak log10(NH) = $peak_log"
fi


# --- Ask user if they want to keep the files ---
echo ""
read -p "Do you want to keep the output files? (1 = yes, 0 = no): " keep_files
echo ""

if [[ "$keep_files" == "1" ]]; then
    echo "Saving output summary..."

    summary_file="$output_dir/output.txt"

    {
        echo "RefleX LOS NH Simulation Summary"
        echo "================================"
        echo ""
        echo "Model used: $model_name"
        echo "Parameter file: $model_file"
        echo ""
        echo "Observing angle: $obs_angle degrees"
        echo "Torus equatorial NH (log10): $torus_nh"
        echo ""
        echo "DIR_Z boundaries:"
        echo "   theta_min = $theta_min°  -> cos = $COSMIN"
        echo "   theta_max = $theta_max°  -> cos = $COSMAX"
        echo ""
        echo "LOS NH (log10): $peak_log"
        echo ""
        echo "Output directory:"
        echo "   $output_dir"
        echo ""
        echo "Log file:"
        echo "   $log_file"
        echo ""
        echo "----------------------------------------------"
        echo "End of summary"
    } > "$summary_file"

    echo "Summary saved in $summary_file"

elif [[ "$keep_files" == "0" ]]; then
    echo "Deleting all output files..."
    rm -rf "$output_dir"
    echo "Output directory deleted."
    echo "NOTE: The LOS NH shown above is not saved."
else
    echo "Invalid input. Keeping output files by default."
fi

echo ""
echo "=============================================================="
echo "Done."
