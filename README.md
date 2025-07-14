#  Low Frequency Extensions of Cyclotron Maser Instability-Generated Radio Emission: A Statistical View of Low Frequency Extensions from Cassini at Saturn

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15879094.svg)](https://doi.org/10.5281/zenodo.15879094)

- __Authors__: Caitríona M. Jackman, Elizabeth O'Dwyer, Simon Walker, Nathan M. Besch

This is the codebase for Jackman et al. (2025), please follow the instructions below to reproduce the figures of the paper. If you only want to access the data find it [here](https://doi.org/10.5281/zenodo.15879094). 

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

Please download the data from [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15879094.svg)](https://doi.org/10.5281/zenodo.15879094) and place it in `data/calculated/`.

Additionally you will need the [Yearly raw Saturn Kilometric Radiation (SKR) files](https://doi.org/10.25935/zkxb-6c84) to be placed in `data/raw/SKR_raw`.

You will then be able to reproduce the figures. If you want to re-create these files from previously obtained datasets, check the next section.

## Data Processing

The new published catalogue and its satellites files are obtained using the scripts in `data_processing/`. To be able to obtain them we need original raw files:

- [Yearly raw Saturn Kilometric Radiation (SKR) files](https://doi.org/10.25935/zkxb-6c84) containing the flux information for the duration of the Cassini mission. Located in `SKR_raw/`.
- [Low Frequency Extensions (LFEs) catalogue](https://doi.org/10.5281/zenodo.8075624) containing LFE start and stop times as well as polygon vertices on the flux map from SKR raw data. Also has a csv file containing start and stop times of LFEs.
- [Phase information](https://figshare.le.ac.uk/articles/dataset/PPO_phases_2004-2017/10201442)

Run `get_ephemeris.py`, `join_lfes.py`, `add_ppos.py`, `join_json.py` and `get_polygon_flux.py` in that order to recreate the files in `data/calculated/`.