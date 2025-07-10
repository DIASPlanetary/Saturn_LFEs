#  Low Frequency Extensions of Cyclotron Maser Instability-Generated Radio Emission: A Statistical View of Low Frequency Extensions from Cassini at Saturn

- __Authors__: Caitríona M. Jackman, Elizabeth O'Dwyer, Simon Walker, Nathan M. Besch

This is the codebase for Jackman et al. (2025), please follow the instructions below to reproduce the figures of the paper. If you only want to access the data find it here [data_zenodo_link](). 

## Installation Steps (recommended)

__Requirements__: git, Python 3.13.1+, environment management system for Python (conda, pyenv...)

Clone the repository in your desired directory:

```
git clone https://github.com/DIASPlanetary/Saturn_LFEs.git
```
We recommend creating a new Python 3.13.1+ environment using your preferred tool. Install the required project packages in your newly created environment:
```
pip install --upgrade pip
pip install -r requirements.txt
```
### SPICE
If you're familiar with using SPICE and spiceypy - and have your own metakernel - you can skip to the end of this section and replace the path with a path to your metakernel. Otherwise please follow the instructions below:

To use spiceypy to quickly retrieve Cassini ephemeris we must download the relevant SPICE kernels. [AutoMeta](https://github.com/mjrutala/AutoMeta) (Rutala, M. J.) is a great package for easily downloading the required kernels without needing any experience with SPICE. It can be downloaded using the following command:

```
git clone https://github.com/mjrutala/AutoMeta
```

Then open a python terminal by typing:

```
python
```
And inside the python terminal run:
```
from make_Metakernel import * make_Metakernel("Cassini")
```

This will download the Cassini kernel files (~3 GB) which may take some time. When finished, you will find a subdirectories `SPICE/Cassini/` which will contain `metakernel_cassini.txt`. Finally,  update the `spice.furnsh("path/to/metakernel")` path in `data_processing/findDetectionPositions.py` with your path to your metakernel.

### Downloading the data

Please download the data folder from [data_zenodo_link]() and place it at the root of the project.

### Configuration file

You can decide to use your own custom paths by editing `config.ini`.

## Data Processing

To create the combined files used in the analysis please start in `data_processing/`. If you only want to reproduce the figures you can ignore this step and skip to the next section.

We will need the following files to be able to create `Joined_LFEs_w_phases.csv`, all located in `data/raw/`:

- [Yearly raw Saturn Kilometric Radiation (SKR) files]() containing the flux information for the duration of the Cassini mission. Located in `SKR_raw/`.
- [Low Frequency Extensions (LFEs) catalogue]() containing LFE start and stop times as well as polygon vertices on the flux map from SKR raw data. Also has a csv file containing start and stop times of LFEs. Located in `unet_output/`.
- [Phase information]() `mag_phases_2004_2007_final.csv`.

`lfe_detections_unet_2874.csv` is generated from matching SPICE data to LFE catalogue data, with the intent of adding XYZ (in KSM) coordinates to the LFE data (see `findDetectionsPositions.py`).

We then need to join LFEs which occur less than 10 minutes apart to give a more accurate scientific picture, done in ` ` creating the file `LFEs_joined.csv`.

Finally we add the phase information in ` ` resulting in the final file `Joined_LFEs_w_phases.csv`.

*what happens with the ephemeris?*

## Figure creation

