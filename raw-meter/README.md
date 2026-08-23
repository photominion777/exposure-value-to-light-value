# A Utopia for RAW Shooters: An Extension from Light Meters to Linear RAW Meters (ETTR)

**Scope:** Models an internal in-camera RAW-metering software logic based on linear sensor limits independently of standard JPEG rendering.

## 📖 Interactive Linear RAW Meter Simulation & Full Article

*   **Simulation:** [Open in Google Colab](https://colab.research.google.com/github/photominion777/exposure-value-to-light-value/blob/main/raw-meter/RAW_Meter_Simulation.ipynb)
*   **Full Article:** [Read the GitHub Wiki](https://github.com/photominion777/exposure-value-to-light-value/wiki/A-Utopia-for-RAW-Shooters%3A-An-Extension-from-Light-Meters-to-Linear-RAW-Meters-%28ETTR%29)

## 🔍 The Core Essence

> [!NOTE]
> **Key Takeaway:** A true RAW exposure meter computes the RAW signal deviation to measure the exact linear distance between the peak signal of the brightest color channel and the sensor's saturation limit.
> 
> * **Input-Driven Physics:** Evaluates raw data strictly at the sensor level based on physical capacity rather than arbitrary mid-gray outputs.
> * **Effective Headroom Tracking:** Accounts for the fixed hardware saturation ceiling and how increased analog gain reduces effective headroom.
> * **SNR Maximization:** Maximizes the signal-to-noise ratio while protecting highlights from clipping.
> * **The Seamless Workflow:** Bridges hardware optimization and in-camera metering through an adjustable artistic bias.

## 🛠️ Proposed Firmware Architecture: The "Snapshot" Workflow

To resolve the engineering dilemmas of continuous sensor-parsing overhead and battery drain during live view, this framework supports a highly efficient, hybrid implementation:

1. **The Static Phase (The Roadmap):** The photographer triggers a single, high-speed linear RAW scan. The system processes this "snapshot" once to map the exact scene boundaries and lock a static RAW histogram.
2. **The Dynamic Phase (The Real-Time Delta):** As the shooter twists the physical aperture, shutter, or ISO dials, the engine **does not redraw** the complex histogram. Instead, it feeds the single locked peak value into the lightweight, additive APEX math engine ($y_i = e_i - av + tv + sv_{\text{raw}}$).
3. **The Tactical Display:** The viewfinder metering needle ($\Delta y_{\text{Display}}$) updates flawlessly in real time at native EVF frame rates with zero processing lag, delivering immediate exposure feedback without thermal compounding or excessive power drain.


### 💻 Companion Code

Run `raw-meter.py` locally:
```bash
python raw-meter.py
```

## 📄 License
Licensed under the **Proprietary Research License** (see [LICENSE](./LICENSE)).
