Caitriona's notes
-----------------
Today can you start on the workflow, documenting each of the steps below. I have identified specific plots that we need to look at together, so we can aim to do this after code club this afternoon.
- Develop sensible workflow from raw files to the final images - like Simon's example shown in code club - so this can be added to GitHub and released with the paper - with one file per figure.
For this, see the messy whiteboard image I sent you on whatsapp...
What do we start with?
- Raw radio data (supercleanflux files in individual years
- Elizabeth O'Dwyer Zenodo files of (i) start/stop times of LFEs, (ii) json files of LFE polygons
- access to SPICE kernels for Cassini to match spacecraft positions to all these radio data and LFE times
THEN onto paper figures

Fig 1: Histogram of LFE delta_t (code to make this should work fine for all, just need to explain a user would need their own config file)

Fig 2: 2-spectrogram plot illustrating joining

THEN need the code to join the LFE list - so we produce (i) LFEs_joined.csv which has the starts/stops and spacecraft position of the joined LFEs, (ii) revised json file with vertices of all the joined polygons

Fig 3: Histogram of LFE duration for the 4553 joined events

Fig 4: Polar plots (3 panels)
[** I will be writing a few lines in the overleaf on the individual bins that we searched where we have reasons to account for higher than surrounding activity **]

Figure 5: *** new figure to add ***
We need to discuss the rho-z map - possibly Monday afternoon when I'm back. I need to have the code to see if I can run it on my machine, and then decide on colour bar, linear vs log scale etc

Figure 6: **to fix the code **
3-panel of histograms of range, local time, latitude. Something funny going on with the normalisation of the LFE occurrence rate. To check what the code is calculating?

Figure 7 onwards...

Then into PPO phase plots. Nathan to share the code to make all these combinations, and Caitriona to check it works on her machine.

These were all for global phase, may need to do local phases as well.

Figure XXX: Average spectrograms for (i) all, (ii) LFEs. Caitriona to check she can run this code locally on her machine.

After that we need to talk about the integrated power calculation. I may want to explore the rapid sheath traversals as a proxy for solar wind compression - and then examine the timeline of integrated power during these...

To Do
-----
- Decide on how to divide the code into folders. think raw data, calculated data, good filenames. some jupyter notebooks might need to be converted to scripts and vice versa. create multiple folders acting as logical sections for the code, especially a divide between "calculatory" code and "analysis/figure" code
- Create a python environment that the user can activate. requirements.txt file
- 