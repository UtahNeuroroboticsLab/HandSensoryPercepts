<!-- README.md -->
# HandSensoryPercepts

A dependency-free web app for recording hand sensory percepts during electrode-pair studies.

URL: https://utahneuroroboticslab.github.io/HandSensoryPercepts/

## Run the app

Open `index.html` in a modern browser. No build step or server is required.

## Default study

The included setup selects channels `00, 01, 03, 04, 05, 06, 07, 08, 09` and generates all 72 directed channel combinations in channel order. Each selected channel is paired with every other selected channel in both directions. Selecting all ten electrodes, including `02`, generates 90 directed combinations. The sidebar can change the electrode pool, polarity rule, hand side, and number of hands before generating a new sequence.

The reference interval starts each block of N stimulus pairs with a numbered reference hand. The default interval of 10 places `REF_01` first, followed by pairs 1 through 10, then `REF_02`, followed by pairs 11 through 20, and so on. Set the interval to `0` to disable reference hands. Reference drawings are cached and exported like stimulus drawings.

Each click on **Save SVG + next -->** downloads the current hand as a true vector SVG and caches its region data in browser storage. **Download cached ZIP** exports the study SVGs, `manifest.csv`, and `study-config.json`.

Created for neuroengineering research by Leonardo M. Ferrisi and contributors.
