import spiceypy as spice
import numpy as np
import pandas as pd
import datetime
import tqdm

#spice.furnsh("SPICE/cassini/metakernel_cassini.txt")
#spice.furnsh("SPICE/cassini/kernels/fk/cas_dyn_v03.tf")
unet_catalogue_csv_fp = 'data/raw/2004001_2017258_start_stop_times.csv'

#   CASSINI end date: Sep. 15 2017
start_datetime = datetime.datetime(2004, 1, 1)
stop_datetime = datetime.datetime(2017, 9, 15, 11, 57) # datetime.datetime(2017, 9, 16)

#   Get an array of datetimes spanning start to stop
minutely_datetimes = np.arange(start_datetime, stop_datetime, datetime.timedelta(minutes=1), dtype = datetime.datetime)

def get_CassiniEphemeris(datetimes):
    """
    Parameters
    ----------
    datetimes : list of datetimes
        A list of python datetimes for which the ephemeris will be returned

    Returns
    -------
    df : pandas DataFrame with columns [datetime, x_KSM, y_KSM, z_KSM, 
                                        subLat, subLon, subLST, R_KSM]
        The Cassini ephemeris for the input datetimes, including:
            - x, y, z, R in the KSM frame
            - the sub-spacecraft Latitude, Longitude, and Local Solar Time (LST)

    """
    #   Load a CASSINI SPICE metakernel
    with spice.KernelPool('SPICE/cassini/metakernel_cassini.txt'):
        
        #   Get SPICE code for Saturn and 3D radii
        target_id = str(spice.bodn2c('Saturn'))
        _, R_S_3 = spice.bodvrd(target_id, 'RADII', 3)
        saturn_flattening = (R_S_3[0] - R_S_3[2]) / R_S_3[0]
        
        #   Convert datetimes to ETs for SPICE
        ets = spice.datetime2et(datetimes)
        
        #   Query the spacecraft position with SPICE
        pos, lt = spice.spkpos('CASSINI', 
                               ets, 
                               'CASSINI_KSM', 
                               'None', 
                               target_id)
        
        sub_lats = []
        sub_lons = []
        sub_lsts = []
        for et in tqdm.tqdm(ets):
            
            #   Get the sub-observer (i.e. spacecraft) point on the target (planet)
            #   This does not handle array inputs, hence the loop
            subpoint, epoch, vec = spice.subpnt('INTERCEPT/ELLIPSOID',  # Method
                                                target_id,              # Saturn
                                                et,                     # When
                                                'IAU_SATURN',           # Frame
                                                'None',                 # Light travel time correction
                                                'CASSINI')              # Observer
            
            #   Convert from rectangular IAU_SATURN coords to planetographic
            lon, lat, alt = spice.recpgr(target_id, 
                                         subpoint, 
                                         R_S_3[0], 
                                         saturn_flattening)
            
            sub_lats.append(lat)
            sub_lons.append(lon)
            
            #   Convert from time to local solar time (LST), given a longitude
            lst_tuple = spice.et2lst(et, 
                                     int(target_id), 
                                     lon, 
                                     'PLANETOGRAPHIC')
            #   Convert local solar time to decimal hours
            decimal_hour_lst = lst_tuple[0] + lst_tuple[1]/60 + lst_tuple[2]/3600
            sub_lsts.append(decimal_hour_lst)
    
    #   Put everything in a dataframe
    df = pd.DataFrame({'start':datetimes,
                       'x_ksm':pos.T[0] / R_S_3[0], 
                       'y_ksm':pos.T[1] / R_S_3[0],
                       'z_ksm':pos.T[2] / R_S_3[0], 
                       'subLat':np.array(sub_lats) * 180/np.pi,
                       'subLon':np.array(sub_lons) * 180/np.pi,
                       'subLST':np.array(sub_lsts)})
    
    #   Calculate the radial distances (this could be done with SPICE, too)
    df['R_ksm'] = np.sqrt(np.sum(df[['x_ksm', 'y_ksm', 'z_ksm']]**2, axis=1))
    
    return df

#   Print this to a csv (this will be pretty hefty)
eph_df = get_CassiniEphemeris(minutely_datetimes)
eph_df.to_csv('data/calculated/20040101000000_20170915115700_ephemeris.csv')

lfe_unet = pd.read_csv(unet_catalogue_csv_fp)
startTimes = lfe_unet["start"]
endTimes = lfe_unet["end"]
labels = lfe_unet["label"]
probability = lfe_unet["probability"]

durations = []
for start, end in zip(startTimes, endTimes):
    start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")
    end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")

    durations.append((end - start).total_seconds())

lfe_starts = [datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') for t in startTimes]
lfe_stops = [datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') for t in endTimes]

lfe_eph_df = get_CassiniEphemeris(lfe_starts)

lfe_unet['start'] = lfe_starts
lfe_unet['end'] = lfe_stops
lfe_detections_unet = lfe_unet.merge(lfe_eph_df, left_on='start', right_on='start', how ='left')

lfe_detections_unet['duration'] = durations

lfe_detections_unet.to_csv('data/calculated/lfe_detections_unet.csv')