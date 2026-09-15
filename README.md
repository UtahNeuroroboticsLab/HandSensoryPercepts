<!-- README.md -->
# HandSensoryPercepts

A dependency-free web app for recording hand sensory percepts during electrode-pair studies.

## Run the app

Open `hand_painter_demo.html` in a modern browser. No build step or server is required.

## Default study

The included setup selects channels `00, 01, 03, 04, 05, 06, 07, 08, 09` and generates all 36 unique choose-2 combinations in channel order. The sidebar can change the electrode pool, polarity rule, hand side, and number of hands before generating a new sequence.

Each click on **Save SVG + next -->** downloads the current hand as a true vector SVG and caches its region data in browser storage. **Download cached ZIP** exports the study SVGs, `manifest.csv`, and `study-config.json`.

Created for neuroengineering research by Leonardo M. Ferrisi and contributors.
