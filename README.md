#  Low Frequency Extensions of Cyclotron Maser Instability-Generated Radio Emission: A Statistical View from Cassini at Saturn

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15979056.svg)](https://doi.org/10.5281/zenodo.15979056)

- __Authors__: Caitríona M. Jackman, Alexandra R. Fogg, Stan W.H. Cowley, Gabrille Provan, Hanna Adamski, Nathan M. Besch, Simon Walker, Matthew J. Rutala, Daragh M. Hollman, Laurent Lamy, Elizabeth P. O'Dwyer

![Example of an LFE plotted over flux](lfe_example.png)

This is the codebase for Jackman et al. (2025), please follow the instructions below to reproduce the figures of the paper. If you only want to access the data find it [here](https://doi.org/10.5281/zenodo.15924636). 

## Installation Steps (recommended)

__Requirements__: git, Python 3.13.1+, environment management system for Python (conda, pyenv...)

Clone the repository in your desired directory:

```
git clone https://github.com/DIASPlanetary/Saturn_LFEs.git
```
We recommend creating a new Python 3.13.1+ environment using your preferred tool. Go into `Saturn_LFEs` and install the required project packages in your newly created environment:
```
pip install --upgrade pip
pip install -r requirements.txt
```

### Download calculated files

Please download the data from [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15979056.svg)](https://doi.org/10.5281/zenodo.15979056) and place the files in `data/calculated/`.

Additionally you will need the [Yearly raw Saturn Kilometric Radiation (SKR) files](https://doi.org/10.25935/zkxb-6c84) to be placed in `data/raw/SKR_raw`.

### Download raw files

These files are to be placed in `data/raw/`

- [Yearly raw Saturn Kilometric Radiation (SKR) files](https://doi.org/10.25935/zkxb-6c84) containing the flux information for the duration of the Cassini mission. Place them in `data/raw/SKR_raw/`.
- [Low Frequency Extensions (LFEs) catalogue](https://doi.org/10.5281/zenodo.8075624) containing LFE start and stop times as well as polygon vertices on the flux map from SKR raw data. Also has a csv file containing start and stop times of LFEs.
- [Phase information](https://figshare.le.ac.uk/articles/dataset/PPO_phases_2004-2017/10201442)

**This is all the setup that is required to reproduce the figures inside `fig` folders.** If you want to re-create the calculated files, check the next section.

## Data Processing

**Please run all python scripts from the `Saturn_LFEs` directory, otherwise the relative file paths will not work.**

To be able to re-create the calculated files i.e. the new LFE catalogue, you will need to download the raw files as stated above as well as setting up SPICE kernels, and then run python scripts in `data_processing/`. Details below.

### SPICE
If you're familiar with using SPICE and spiceypy - and have your own metakernel - you can skip to the end of this section and replace the path with a path to your metakernel. Otherwise please follow the instructions below:

To use spiceypy to quickly retrieve Cassini ephemeris we must download the relevant SPICE kernels. [AutoMeta](https://github.com/mjrutala/AutoMeta) (Rutala, M. J.) is a great package for easily downloading the required kernels without needing any experience with SPICE. In `Saturn_LFEs` directory execute this command:

```
git clone https://github.com/mjrutala/AutoMeta.git
```

Then run:

```
python Autometa/autometa/make_Metakernel.py
```
And when prompted with typing the name of the spacecraft simply type:
```
Cassini
```
And press `Enter`. Then press `Enter` again to download the SPICE folder at the root directory of `Saturn_LFEs`.

This will download the Cassini kernel files (~3 GB) in a SPICE folder at the root of the project. When finished, you will find a subdirectory `SPICE/Cassini/` which will contain `metakernel_cassini.txt`.

### Final Steps

Run `get_ephemeris.py`, `join_lfes.py`, `add_ppos.py`, `join_json.py` and `get_polygon_flux.py` in that order to recreate the files in `data/calculated/`.
