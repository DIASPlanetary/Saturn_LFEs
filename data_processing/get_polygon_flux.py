import numpy as np
import xarray as xr

import matplotlib.dates as mdates
from matplotlib.path import Path

from tfcat import TFCat

from tqdm import tqdm
from multiprocess import Pool  # Change 'multiprocess' to 'multiprocessing' if given an error

from lfe_func import get_sav_data, get_poly_coords

# Filepaths
unet_catalogue_fp = 'data/raw/2004001_2017258_catalogue.json'
skr_poly_flux_fp = 'data/calculated/skr_poly_flux'

# Import all Polygon Time Frequency Coordinates and put them in a list
catalogue = TFCat.from_file(unet_catalogue_fp)

poly_tf_list = []
for i in range(4874):
    poly_time, poly_freq = np.array(catalogue._data['features'][i]['geometry']['coordinates'][0]).T

    poly_time = poly_time.astype('datetime64[s]')

    poly_tf = np.array([mdates.date2num(poly_time), poly_freq]).T

    poly_tf_list.append(poly_tf)

def create_mask(poly_coords):
    """Create a flux mask given polygon coordinates.

    Parameters
    ----------
    poly_coords: list
        List of polygon time-frequency coordinates.
    
    Returns
    -------
    mask: numpy.array
        Boolean mask of dimension flux where True values represent polygon coordinates in the flux.
    """
    freq_grid, time_grid = np.meshgrid(freq, mdates.date2num(time), indexing='ij')
    points = np.vstack((time_grid.flatten(), freq_grid.flatten())).T

    path = Path(poly_coords)
    mask_flat = path.contains_points(points)
    mask = mask_flat.reshape(flux.shape)

    return mask

# Loop over every mission year to get yearly files of masked flux w.r.t polygon coordinates, time and frequency. The dimensions of these arrays are similar to sav data files.

# A parallelization process is used, **BE CAREFUL ABOUT CPU_NUM VARIABLE**, and each year has a progress bar.

for year in range(2004, 2018):
    print(year)
    
    time, freq, flux = get_sav_data(year)
    poly_coordinates = get_poly_coords(year, poly_tf_list)

    cpu_num = 9
    mask_list = []

    max_ = len(poly_coordinates)
    with Pool(cpu_num) as p, tqdm(total=max_) as pbar:
        for result in p.imap(create_mask, poly_coordinates):
            pbar.update()
            pbar.refresh()
            mask_list.append(result)

    combined_mask = np.sum(mask_list, axis=0).astype(bool)

    masked_flux = flux.copy()
    masked_flux[~combined_mask] = np.nan

    da = xr.DataArray(masked_flux, dims=['frequency', 'time'], coords= {'frequency': (['frequency'], freq), 'time':(['time'], time)}, name='flux')

    da.to_netcdf(skr_poly_flux_fp + f'/poly_flux_{year}.ncdf')

# Add code to combine the file and delete intermediate files

