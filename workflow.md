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

- How do you want to deal with SPICE? was thinking: change spice path to your own files or download the relevant spice kernels using this githu repo |link to Matt's Autometa|
- Before I can do anything else I will need to know the exact workflow of the code
- Where is the data stored, how does it integrate with the code base

CODE TO BE CHANGED
------------------
- deal with the different name of 2017 sav file in lfe_func
- recalculate polyflux using the joined LFEs and add code snippet that combines the file
- name variable in polyflux combined as flux when first saving
- change get_polygon_flux to python script