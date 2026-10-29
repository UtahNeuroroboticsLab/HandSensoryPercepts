<!-- README.md -->
# HandSensoryPercepts

A dependency-free web app for configuring electrode stimulation studies, recording hand sensory percepts, and exporting study-ready vector files.

URL: https://utahneuroroboticslab.github.io/HandSensoryPercepts/

## Run the app

Open `index.html` in a modern browser. No build step or server is required.

## Configure a study

The left panel lets you choose the hand side, stimulation mode, sweep mode, participating electrodes, and study size. The app supports 16 electrodes, `Ch00` through `Ch15`; all 16 are selected in the initial setup. Change the electrode checkboxes to include only the channels needed for a study.

### Choose-2 and Choose-3

- **Choose-2** assigns one electrode as the anode and one as the cathode. The **First channel role** control chooses the role of the first channel in a pair. This control is hidden for Choose-3.
- **Choose-3** assigns two electrodes as anodes and one as a cathode. The app displays both anodes and the cathode for each stimulus combination. Polarity swapping is unavailable for Choose-3 so each item keeps its one-cathode/two-anode assignment.

### Full sweep and Unique only

- **Full sweep** includes all polarity assignments. For Choose-2, both orientations of each channel pair are included. For Choose-3, each three-channel set appears three times, once for each possible cathode.
- **Unique only** includes one polarity assignment for each channel set. For Choose-2, each pair appears once, with its first channel's role controlled by **First channel role**. For Choose-3, each three-channel set appears once; the lowest-numbered channel in the set is the cathode and the other two are anodes.

The number of possible stimulus combinations depends on the number of selected channels, `n`:

| Mode | Full sweep | Unique only |
|---|---:|---:|
| Choose-2 | `n × (n − 1)` | `n × (n − 1) ÷ 2` |
| Choose-3 | `n × (n − 1) × (n − 2) ÷ 2` | `n × (n − 1) × (n − 2) ÷ 6` |

For 10 selected channels, Choose-2 produces 90 full-sweep pairs or 45 unique pairs. Choose-3 produces 360 full-sweep combinations or 120 unique combinations. With all 16 channels selected, the corresponding counts are 240 or 120 for Choose-2, and 1,680 or 560 for Choose-3.

The study limit can be used to generate fewer than all available combinations. The summary updates the possible combination count and estimated total hands as you change the mode, sweep, selected channels, study limit, or reference interval.

## References and study sequence

The reference interval inserts a numbered reference hand before each block of N stimulus combinations. It defaults to 10; set it to `0` to disable reference hands. For example, `REF_01` is placed before combinations 1–10, then `REF_02` before combinations 11–20.

The initial configuration is Choose-2 with Full sweep, all 16 channels selected, the first channel assigned as the anode, and a reference interval of 10.

## Save and export

Each click on **Save SVG + next -->** downloads the current hand as a true vector SVG and caches its region data in browser storage. **Download cached ZIP** exports the study SVGs, `manifest.csv`, and `study-config.json`.

Stimulus SVG metadata and the manifest identify the pairing and sweep modes and record the anode channel(s) and cathode. Choose-3 exports include both anodes. Reference drawings are cached and exported like stimulus drawings.

Created for neuroengineering research by Leonardo M. Ferrisi and contributors.
