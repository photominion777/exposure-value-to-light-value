"""
LINEAR RAW EXPOSURE METER SIMULATOR (CLI & VISUAL SENSOR DASHBOARD)
Proprietary Framework - Copyright © 2026 photominion777. All rights reserved.
"""

# ===================================================================================================
# STANDALONE LINEAR RAW ENGINE (PART 1: PARAMETER CONFIGURATION & LIGHTING LOGIC)
# ===================================================================================================
import math
import numpy as np
import matplotlib.pyplot as plt

# 🛠️ CONFIGURE YOUR SIMULATION INPUT VALUES HERE DIRECTLY:
SCENE_RADIANCE = 4096.0  # Helligkeit der Szene
APERTURE_N     = 16      # Blende f/16 (Sunny 16 Regel)
SHUTTER_T      = "1/125" # Verschlusszeit
ISO_S          = 100     # ISO-Verstärkung
BIT_DEPTH      = 14      # Sensor-Auflösung (12, 14, 16)
ARTISTIC_BIAS  = 0       # Exposure Compensation Index (-9 bis +9)

# Global option lists representing the manufacturer display values
N_OPTIONS = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 2.8, 3.2, 3.5, 4.0, 4.5, 5.0, 5.6, 6.3, 7.1, 8.0, 9.0, 10, 11, 13, 14, 16, 18, 20, 22, 25, 29, 32]
T_OPTIONS = ["1", "1/1.3", "1/1.6", "1/2", "1/2.5", "1/3.2", "1/4", "1/5", "1/6", "1/8", "1/10", "1/13", "1/15", "1/20", "1/25", "1/30", "1/40", "1/50", "1/60", "1/80", "1/100", "1/125", "1/160", "1/200", "1/250", "1/320", "1/400", "1/500", "1/640", "1/800", "1/1000", "1/1250", "1/1600", "1/2000", "1/2500", "1/3200", "1/4000", "1/5000", "1/6400", "1/8000"]
S_OPTIONS = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800, 16000, 20000, 25600, 51200, 102400]

def get_lighting_name(lv):
    ranges = [
        (19.5, 22.5, "Industrial Laser / Lab Light"), (18.5, 19.5, "Arc Welding / High-Power LED"),
        (17.0, 18.5, "Studio Flash / Searchlight"), (15.5, 17.0, "Extreme Sun (Snow/Sand)"),
        (14.5, 15.5, "Sunny"), (13.5, 14.5, "Hazy Sun"), (12.5, 13.5, "Bright Overcast"),
        (11.5, 12.5, "Overcast / Cloudy"), (10.5, 11.5, "Deep Shade"), (9.5, 10.5, "Sunset / Sunrise"),
        (8.5, 9.5, "Very Dynamic Twilight"), (7.5, 8.5, "Bright Street Lighting"),
        (6.5, 7.5, "Blue Hour / City Night"), (5.5, 6.5, "Bright Indoor"), (4.5, 5.5, "Standard Indoor"),
        (3.5, 4.5, "Living Room (Evening)"), (2.5, 3.5, "Dim Indoor"), (1.5, 2.5, "Distant Building Lights"),
        (0.5, 1.5, "Very Dim Interior"), (-0.5, 0.5, "Night Sky / City Skyline"),
        (-1.5, -0.5, "Dim Night Street"), (-2.5, -1.5, "Full Moon (Snow)"),
        (-3.5, -2.5, "Full Moon (Landscape)"), (-4.5, -3.5, "Quarter Moon"),
        (-5.5, -4.5, "Crescent Moon"), (-7.5, -5.5, "Starlight Night")
    ]
    for low, high, name in ranges:
        if low <= lv < high: return name
    return "Transition / Mixed Light"

# ===================================================================================================
# STANDALONE LINEAR RAW ENGINE (PART 2: SENSOR MATHEMATICS & LINEAR INTEGRATION)
# ===================================================================================================
# 1. Map values to exact mathematical APEX log steps
idx_N, idx_t, idx_S = N_OPTIONS.index(APERTURE_N), T_OPTIONS.index(SHUTTER_T), S_OPTIONS.index(ISO_S)
N_exact = 1.0 * (2**(1/6))**(idx_N - 3)
t_exact = 1.0 * (2**(-1/3))**idx_t
S_exact = 100.0 * (2**(1/3))**(idx_S - 3)

K = 12.5
LV_ext = math.log2((100.0 * SCENE_RADIANCE) / K) if SCENE_RADIANCE > 0 else -5.0
lighting_condition = get_lighting_name(LV_ext)

Y_sat = (2**BIT_DEPTH) - 1
y_sat = math.log2(Y_sat)

av = math.log2(N_exact**2)
tv = math.log2(t_exact)
sv_raw = math.log2(S_exact / 100.0)

analog_hardware_base = 3.00
kappa_log2 = analog_hardware_base + math.log2(2**BIT_DEPTH - 1)
photometric_correction = math.log2(K / 100.0)

e_peak = kappa_log2 + LV_ext + photometric_correction
y_peak = e_peak - av + tv + sv_raw
Y_peak_linear = 2**y_peak

delta_y_ETTR = y_peak - y_sat
ec_user = ARTISTIC_BIAS * (1.0 / 3.0)
delta_y_Display = delta_y_ETTR - ec_user

scale_header = " -5       -4       -3       -2       -1        0       +1       +2       +3       +4       +5  "
scale_ticks = []
for index in range(-15, 16):
    tick_value = index / 3.0
    if abs(delta_y_Display - tick_value) < (1.0 / 6.0) and -5.1 < delta_y_Display < 5.1:
        scale_ticks.append("▲")
    elif index % 3 == 0: scale_ticks.append("|")
    else: scale_ticks.append("·")

scale_visual = ("◀ " if delta_y_Display < -5.1 else "  ") + "  ".join(scale_ticks) + (" ▶" if delta_y_Display > 5.1 else "  ")
clipping_ratio = (Y_peak_linear / Y_sat) * 100.0

if Y_peak_linear <= Y_sat:
    percentage_pixel_clipping = 0.0
else:
    x_vals_calc = np.linspace(0, Y_peak_linear * 1.5, 5000)
    sigma_calc = Y_peak_linear * 0.22
    y_hist_calc = np.exp(-((x_vals_calc - Y_peak_linear * 0.8)**2) / (2 * sigma_calc**2)) * 0.6 + \
                  np.exp(-((x_vals_calc - Y_peak_linear * 0.3)**2) / (2 * (sigma_calc * 1.5)**2)) * 0.5 + \
                  np.exp(-((x_vals_calc - Y_peak_linear * 0.95)**2) / (2 * (sigma_calc * 0.40)**2)) * 0.35
    total_area = np.trapezoid(y_hist_calc, x_vals_calc)
    clipped_mask = x_vals_calc > Y_sat
    percentage_pixel_clipping = (np.trapezoid(y_hist_calc[clipped_mask], x_vals_calc[clipped_mask]) / total_area) * 100.0

total_sensor_pixels = 24000000
absolute_clipped_pixels = int((percentage_pixel_clipping / 100.0) * total_sensor_pixels)
clipped_mpx = absolute_clipped_pixels / 1_000_000
total_mpx = total_sensor_pixels / 1_000_000

# ===================================================================================================
# STANDALONE LINEAR RAW ENGINE (PART 3: ASCII TERMINAL PRINT & HISTOGRAM GRAPH GENERATION)
# ===================================================================================================
print(f"""===================================================================================================
[ INTERNAL LINEAR RAW METER SIMULATION - RSI PARSING ENGINE ]
===================================================================================================
Sensor ADC Bit-Depth Resolution    :  {BIT_DEPTH}-bit Domain
Absolute Saturation Limit (Y_sat)  :  {Y_sat:,} Digital Numbers (DN) [Constant Hardware Ceiling]
Peak Linear Channel Signal (Y_peak):  {min(int(Y_peak_linear), Y_sat):,} DN {"[🚨 CLIPPED AT HARDWARE WALL]" if Y_peak_linear > Y_sat else ""}
---------------------------------------------------------------------------------------------------
RAW Sensor Log Ceiling (y_sat)     :  {math.log2(Y_sat):.2f} stops [Constant Hardware Baseline]
Environmental Light Value (LV_ext) :  {LV_ext:.2f} (Reflects: {lighting_condition})
ADC Range Utilization              :  {clipping_ratio:.1f}%
---------------------------------------------------------------------------------------------------
[ERGONOMIC LIVE PIXEL CLIPPING METRICS]
Absolute Pixel Clipping            :  {clipped_mpx:.2f} Mpx / {total_mpx:.0f} Mpx
Percentage Pixel Clipping          :  {percentage_pixel_clipping:.2f} % of Sensor Area
---------------------------------------------------------------------------------------------------
RAW Signal Index (delta_y_display) :  {delta_y_Display:+.2f} Stops (Normed: 0 RSI = 12.5% Saturation)
User Artistic Override (EC_user)   :  {ec_user:+.2f} Stops
---------------------------------------------------------------------------------------------------
Displayed RAW Viewfinder Index (delta_y_display): {delta_y_Display:+.2f} Stops

{scale_header}
{scale_visual}
===================================================================================================
""")

# Render and Save the Matplotlib Histogram without requiring local display servers
fig, ax1 = plt.subplots(figsize=(11, 4.5))
rsi_ticks = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
rsi_sat = 3.0
x_rsi = np.linspace(-5.2, 5.2, 1500)
x_linear_map = Y_sat * (2**(x_rsi - rsi_sat))

sigma = Y_peak_linear * 0.22
y_hist = np.exp(-((x_linear_map - Y_peak_linear * 0.8)**2) / (2 * sigma**2)) * 0.6 + \
         np.exp(-((x_linear_map - Y_peak_linear * 0.3)**2) / (2 * (sigma * 1.6)**2)) * 0.5 + \
         np.exp(-((x_linear_map - Y_peak_linear * 0.95)**2) / (2 * (sigma * 0.40)**2)) * 0.35

if Y_peak_linear > Y_sat:
    y_hist[x_rsi > rsi_sat] = 0.0

ax1.fill_between(x_rsi, 0, y_hist, where=(x_rsi <= rsi_sat), color='#2ca02c', alpha=0.6, label=f'Valid RAW Sensor Data ({100.0 - percentage_pixel_clipping:.2f}%)')
if percentage_pixel_clipping > 0.01:
    clip_box_x = x_rsi[(x_rsi >= rsi_sat - 0.05) & (x_rsi <= rsi_sat)]
    ax1.fill_between(clip_box_x, 0, 0.1 + (percentage_pixel_clipping / 100.0) * 0.9, color='#d62728', alpha=0.85, label='CRITICAL: Clipping')

ax1.scatter(rsi_sat, 0.03, color='black', marker='^', s=120, zorder=5)
ax1.scatter(rsi_sat, 1.07, color='black', marker='v', s=120, zorder=5, clip_on=False)

# FIXED: Removed the redundant ax1.set_xscale('log') call to eliminate negative limit warnings

dn_labels = [str(int(round(Y_sat * (2**(r - rsi_sat))))) for r in rsi_ticks]
ax1.set_xticks(rsi_ticks)
ax1.set_xticklabels(dn_labels, fontsize=9)
ax1.set_xlim(-5.2, 5.2)
ax1.set_ylim(0, 1.1)
ax1.set_xlabel('Linear Digital Signal Level [Digital Numbers (DN)]', fontsize=10, labelpad=8)
ax1.set_ylabel('Pixel Distribution Frequency', fontsize=10, labelpad=8)
ax1.grid(True, linestyle=':', alpha=0.6)

ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks(rsi_ticks)
ax2.set_xticklabels([f"{r:+} RSI" if r != 0 else "0 RSI" for r in rsi_ticks], fontsize=9, color='#2980b9')
ax2.set_xlabel('Raw Signal Index [RSI] Scale in Stops', fontsize=10, color='#2980b9', labelpad=8)

info_text = f"Clipped Pixels:\n{clipped_mpx:.2f} Mpx / {total_mpx:.0f} Mpx\n({percentage_pixel_clipping:.2f}%)"
props = dict(boxstyle='round,pad=0.3', facecolor='#d62728' if percentage_pixel_clipping > 0 else '#2ca02c', alpha=0.15, edgecolor='none')
ax1.text(rsi_sat + 0.2, 0.82, info_text, fontsize=9, fontweight='bold', color='#c0392b' if percentage_pixel_clipping > 0 else '#27ae60', ha='left', va='center', bbox=props)

plt.title(f'VISUAL SENSOR DASHBOARD ({BIT_DEPTH}-bit Domain)', fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()

# Save the final file locally or output via the integrated plot engine
plt.savefig('raw_histogram.png', dpi=150)
plt.show()

