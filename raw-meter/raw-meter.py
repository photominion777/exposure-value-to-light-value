"""
LINEAR RAW EXPOSURE METER SIMULATOR (CLI & VISUAL SENSOR DASHBOARD)
Proprietary Framework - Copyright © 2026 photominion777. All rights reserved.
"""
import math
import numpy as np
import matplotlib.pyplot as plt

# =========================================================================
# [ PLEASE ENTER INPUT VALUES HERE ]
# =========================================================================
DEFAULT_LUMINANCE = 4096.0  # Physical Scene Peak Luminance in cd/m²
DEFAULT_APERTURE = 16.0     # Aperture f-number (N)
DEFAULT_SHUTTER = "1/125"   # Shutter speed (t) as a string
DEFAULT_ISO = 100.0         # ISO speed rating (S)
DEFAULT_BIT_DEPTH = 14      # Sensor ADC Bit-Depth Resolution (12, 14, or 16)
DEFAULT_EC = 0.0            # Artistic Bias / Exposure Compensation (stops)
# =========================================================================

# Global option lists representing the manufacturer display values
N_OPTIONS = [
    0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 2.8, 3.2,
    3.5, 4.0, 4.5, 5.0, 5.6, 6.3, 7.1, 8.0, 9.0, 10, 11, 13, 14, 16, 18,
    20, 22, 25, 29, 32
]
T_OPTIONS = [
    "1", "1/1.3", "1/1.6", "1/2", "1/2.5", "1/3.2", "1/4", "1/5", "1/6",
    "1/8", "1/10", "1/13", "1/15", "1/20", "1/25", "1/30", "1/40", "1/50",
    "1/60", "1/80", "1/100", "1/125", "1/160", "1/200", "1/250", "1/320",
    "1/400", "1/500", "1/640", "1/800", "1/1000", "1/1250", "1/1600",
    "1/2000", "1/2500", "1/3200", "1/4000", "1/5000", "1/6400", "1/8000"
]
S_OPTIONS = [
    6.25, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0, 40.0, 50.0, 64.0, 80.0, 100.0,
    125.0, 160.0, 200.0, 250.0, 320.0, 400.0, 500.0, 640.0, 800.0, 1000.0,
    1250.0, 1600.0, 2000.0, 2500.0, 3200.0, 4000.0, 5000.0, 6400.0, 8000.0,
    10000.0, 12500.0, 16000.0, 20000.0, 25600.0, 51200.0, 102400.0, 204800.0,
    409600.0, 819200.0
]
BIT_DEPTH_OPTIONS = [12, 14, 16]

# Generate exact radiance values matching original logic
RADIANCE_OPTIONS = []
for index in range(-18, 67):
    l_phys = (2**(index/3.0)) / (100 / 12.5)
    if l_phys >= 10:
        l_phys = round(l_phys, 1)
    else:
        l_phys = round(l_phys, 2)
    if l_phys not in RADIANCE_OPTIONS:
        RADIANCE_OPTIONS.append(l_phys)


def get_lighting_name(lv):
    ranges = [
        (19.5, 22.5, "Industrial Laser / Lab Light"), (18.5, 19.5, "Arc Welding / High-Power LED"),
        (17.0, 18.5, "Studio Flash / Searchlight"), (15.5, 17.0, "Extreme Sun (Snow/Sand)"),
        (14.5, 15.5, "Sunny"), (13.5, 14.5, "Hazy Sun"),
        (12.5, 13.5, "Bright Overcast"), (11.5, 12.5, "Overcast / Cloudy"),
        (10.5, 11.5, "Deep Shade"), (9.5, 10.5, "Sunset / Sunrise"),
        (8.5, 9.5, "Very Dynamic Twilight"), (7.5, 8.5, "Bright Street Lighting"),
        (6.5, 7.5, "Blue Hour / City Night"), (5.5, 6.5, "Bright Indoor"),
        (4.5, 5.5, "Standard Indoor"), (3.5, 4.5, "Living Room (Evening)"),
        (2.5, 3.5, "Dim Indoor"), (1.5, 2.5, "Distant Building Lights"),
        (0.5, 1.5, "Very Dim Interior"), (-0.5, 0.5, "Night Sky / City Skyline"),
        (-1.5, -0.5, "Dim Night Street"), (-2.5, -1.5, "Full Moon (Snow)"),
        (-3.5, -2.5, "Full Moon (Landscape)"), (-4.5, -3.5, "Quarter Moon"),
        (-5.5, -4.5, "Crescent Moon"), (-7.5, -5.5, "Starlight Night")
    ]
    for low, high, name in ranges:
        if low <= lv < high:
            return name
    return "Transition / Mixed Light"

# ===================================================================================================
# LINEAR RAW EXPOSURE METER SIMULATOR (PART 2: CALCULATION CORE & CLI RENDERING)
# ===================================================================================================
def execute_linear_raw_meter(L_input, N, t_str, S, bit_depth, ec_user):
    idx_N = N_OPTIONS.index(N)
    idx_t = T_OPTIONS.index(t_str)
    idx_S = S_OPTIONS.index(S)
    
    N_exact = 1.0 * (2**(1/6))**(idx_N - 3)
    t_exact = 1.0 * (2**(-1/3))**idx_t
    # CALIBRATION FIX: ISO 100 sits at index 12 in the full array, shift is -12
    S_exact = 100.0 * (2**(1/3))**(idx_S - 12)

    L_eff_peak = float(L_input)
    K = 12.5

    if L_eff_peak > 0:
        LV_ext = math.log2((100.0 * L_eff_peak) / K)
    else:
        LV_ext = -5.0
        
    lighting_name = get_lighting_name(LV_ext)
    Y_sat = (2**bit_depth) - 1
    y_sat = math.log2(Y_sat)

    av = math.log2(N_exact**2)
    tv = math.log2(t_exact)
    sv_raw = math.log2(S_exact / 100.0)

    analog_hardware_base = 3.00
    kappa_log2 = analog_hardware_base + math.log2(2**bit_depth - 1)
    photometric_correction = math.log2(K / 100.0)

    e_peak = kappa_log2 + LV_ext + photometric_correction
    y_peak = e_peak - av + tv + sv_raw
    Y_peak_linear = 2**y_peak

    delta_y_ETTR = y_peak - y_sat
    delta_y_Display = delta_y_ETTR - ec_user

    # Build the ASCII viewfinder scale matrix (Absolute Grid Lock)
    scale_hdr_ticks = []
    scale_ticks = []
    
    for index in range(-15, 16):
        tick_value = index / 3.0
        
        if index % 3 == 0:
            val_num = int(tick_value)
            if val_num > 0:
                scale_hdr_ticks.append(f"+{val_num}")
            elif val_num < 0:
                scale_hdr_ticks.append(str(val_num))
            else:
                scale_hdr_ticks.append(" 0")
        else:
            scale_hdr_ticks.append("  ")
            
        if index == -15 and delta_y_Display < -5.1:
            scale_ticks.append(" ◀")
        elif index == 15 and delta_y_Display > 5.1:
            scale_ticks.append(" ▶")
        elif abs(delta_y_Display - tick_value) < (1.0 / 6.0):
            scale_ticks.append(" ▲")
        elif index % 3 == 0:
            scale_ticks.append(" |")
        else:
            scale_ticks.append(" ·")

    scale_hdr = "   " + "".join(scale_hdr_ticks)
    scale_vis = "   " + "".join(scale_ticks)
    clipping_ratio = (Y_peak_linear / Y_sat) * 100.0

    # Render Terminal Output Stream
    clip_msg = "[🚨 CLIPPED AT HARDWARE WALL]" if Y_peak_linear > Y_sat else ""
    output_text = f"""==================================================
[ INTERNAL LINEAR RAW METER SIMULATION TERMINAL ]
===========================================================================
Sensor ADC Bit-Depth Resolution    :  {bit_depth}-bit Domain
Absolute Saturation Limit (Y_sat)  :  {Y_sat:,} DN [Constant]
Peak Linear Channel Signal (Y_peak):  {min(int(Y_peak_linear), Y_sat):,} DN {clip_msg}
---------------------------------------------------------------------------
RAW Sensor Log Ceiling (y_sat)     :  {y_sat:.2f} stops [Constant Baseline]
Environmental Light Value (LV_ext) :  {LV_ext:.2f} (Reflects: {lighting_name})
Digital Capacity Utilization       :  {clipping_ratio:.1f}%
---------------------------------------------------------------------------
True RAW ETTR Deviation (Δy_ETTR)  : {delta_y_ETTR:+.2f} stops
User Exposure Override (EC_user)   : {ec_user:+.2f} stops
---------------------------------------------------------------------------
Displayed RAW Meter Indicator (Δy_Display): {delta_y_Display:+.2f} stops

{scale_hdr}
{scale_vis}
===========================================================================
"""
    if Y_peak_linear > Y_sat:
        output_text += f"🚨 CRITICAL HARDWARE CLIPPING: Exceeds sensor " \
                       f"capacity by {delta_y_ETTR:.2f} f-stops.\n"
    elif abs(delta_y_ETTR) < 0.01:
        output_text += "✅ OPTIMAL ETTR EXPOSURE: Perfect sensor utilization."
    else:
        output_text += f"⚠️ UNDERUTILIZED DYNAMIC RANGE: Leaving " \
                       f"{abs(delta_y_ETTR):.2f} f-stops of safety headroom."

    print(output_text)

      # =========================================================================
    # [ DRAW VISUAL SENSOR DASHBOARD VIA MATPLOTLIB ]
    # =========================================================================
    plt.figure(figsize=(11, 5))
    x_vals = np.linspace(0, Y_sat * 1.5, 1000)
    sigma = Y_peak_linear * 0.25

    # Split GMM into super short variables to avoid PEP 8 line length errors
    gmm_mid = np.exp(-((x_vals - Y_peak_linear * 0.8)**2) / (2 * sigma**2))
    gmm_shd = np.exp(-((x_vals - Y_peak_linear * 0.3)**2) / (2 * (sigma * 1.5)**2))
    gmm_hgt = np.exp(-((x_vals - Y_peak_linear)**2) / (2 * (sigma * 0.1)**2))

    y_hist = gmm_mid * 0.7 + gmm_shd * 0.4 + gmm_hgt * 0.3

    # Green STRICTLY stops and cuts off right at the wall
    plt.fill_between(
        x_vals, 0, y_hist, where=(x_vals <= Y_sat),
        color='#2ca02c', alpha=0.6, label='Valid RAW Data'
    )
    
    # TOLERANCE PUFFER LOCK: Red only triggers if peak actively exceeds wall by +50.0 DN
    tolerance_puffer = 50.0
    if Y_peak_linear > (Y_sat + tolerance_puffer):
        plt.fill_between(
            x_vals, 0, y_hist, where=(x_vals > Y_sat),
            color='#d62728', alpha=0.6, label='CRITICAL: Clipping'
        )

    # Draw Wall
    plt.axvline(
        x=Y_sat, color='red', linestyle='--', linewidth=2,
        label=f'Hardware Wall (Y_sat: {Y_sat:,} DN)'
    )

    # DYNAMISCHER TITEL: Zeigt die gewählte Domain und die echte Sättzungswand live
    plt.title(
        f'VISUAL SENSOR DASHBOARD ({bit_depth}-bit Domain)\n'
        f'Physical Signal Distribution (Max Capacity: {Y_sat:,} DN)', 
        fontsize=12, fontweight='bold', pad=15
    )
    
    # DYNAMISCHE ACHSE: Macht die Bit-Invarianz der Kurve didaktisch verständlich
    plt.xlabel(
        f'Linear Sensor Signal Level [0 to {Y_sat:,} Digital Numbers (DN)]',
        fontsize=10, labelpad=8
    )
    
    plt.ylabel('Pixel Distribution Frequency', fontsize=10, labelpad=8)
    plt.xlim(0, Y_sat * 1.3)
    plt.ylim(0, 1.1)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left', frameon=True)

    plt.tight_layout()
    print("\n[Rendering visual histogram window... Close window to exit.]")
    plt.show()


if __name__ == "__main__":
    execute_linear_raw_meter(
        L_input=DEFAULT_LUMINANCE,
        N=DEFAULT_APERTURE,
        t_str=DEFAULT_SHUTTER,
        S=DEFAULT_ISO,
        bit_depth=DEFAULT_BIT_DEPTH,
        ec_user=DEFAULT_EC
    )
