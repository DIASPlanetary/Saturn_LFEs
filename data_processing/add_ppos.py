import numpy as np
import pandas as pd

from scipy.io import readsav
from tqdm import tqdm

data_directory = 'data/calculated/'
ppo_file = 'data/raw/mag_phases_2004_2017_final.sav' # Phases Calibration Data

join_unet = pd.read_csv('data/calculated/LFEs_joined.csv', index_col = 0)

def SavePPO(file_path, LFE_df, data_directory, file_name):
    """Read PPO phase sav file, and matching lfe start with the PPOs."""
    print("Finding LFE Phase")

    print(f"Loading {file_path}")
    ppo_df = readsav(file_path)


    south_time = ppo_df["south_model_time"] # minutes since 2004-01-01 00:00:00
    south_phase = ppo_df["south_mag_phase"]

    north_time = ppo_df["north_model_time"]
    north_phase = ppo_df["north_mag_phase"]

    doy2004_0 = pd.Timestamp(2004, 1, 1)

    lfe_south_phase_indices = []
    lfe_north_phase_indices = []
    for i, lfe in tqdm(LFE_df.iterrows(), total=len(LFE_df)):

        lfe_start_time = lfe["start"] # pandas timestamp
        lfe_start_doy2004 = (pd.Timestamp(lfe_start_time) - doy2004_0).total_seconds() / 60 / 60 / 24 # days since 2004-01-01 00:00:00

        # Find minimum time difference
        south_index = (np.abs(south_time - lfe_start_doy2004)).argmin()
        lfe_south_phase_indices.append(south_index)

        north_index = (np.abs(north_time - lfe_start_doy2004)).argmin()
        lfe_north_phase_indices.append(north_index)


    print(len(lfe_south_phase_indices))
    LFE_df["south phase"] = np.array(south_phase)[lfe_south_phase_indices]
    LFE_df["north phase"] = np.array(north_phase)[lfe_north_phase_indices]

    print(f"Saving new csv file to {data_directory+file_name}")
    LFE_df.to_csv(data_directory + file_name)

SavePPO(ppo_file, join_unet, data_directory, "Joined_LFEs_w_phases.csv")