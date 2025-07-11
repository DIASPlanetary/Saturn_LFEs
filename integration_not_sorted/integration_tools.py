#%% Imports
import pandas as pd
import numpy as np

#%% Definitions

def fit_pandas(df, sweep, frequency, flux):
    """
    Computes linear segments by calculating slopes and intercepts between consecutive frequency-flux pairs.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing sweep, frequency, and flux data.
    sweep : str
        Column name representing sweep identifiers.
    frequency : str
        Column name representing frequency values.
    flux : str
        Column name representing flux values.

    Returns
    -------
    pd.DataFrame
        DataFrame with calculated slopes, intercepts, and frequency segment boundaries.

    Example
    -------
    >>> df = pd.DataFrame({"sweep": [1, 1, 1], "frequency": [10, 20, 30], "flux": [5, 10, 15]})
    >>> fit_pandas(df, "sweep", "frequency", "flux")
    """
    freqs, flux = df[[frequency, flux]].values.T  # Extract frequency and flux as separate arrays
    slopes = np.diff(flux) / np.diff(freqs)  # Compute slopes between consecutive points
    intercepts = flux[:-1] - slopes * freqs[:-1]  # Compute intercepts based on slope and frequency
    
    return pd.DataFrame({
        sweep: df[sweep].iloc[0],  # Assign the sweep value to each row
        'intercept': intercepts,  # Store computed intercept values
        'slope': slopes,  # Store computed slope values
        'f1': freqs[:-1],  # Store the first frequency of each segment
        'f2': freqs[1:]  # Store the second frequency of each segment
    })

def linear_segments(df, time='datetime_ut', frequency='FREQ', sweep='SWEEP', flux='AMPL_Z', 
                    preserve_cols=['sweep_start_date'], preserve_funcs=['min', 'max', 'median'],
                    preserve_col_suffix=[]):
    """
    Processes a DataFrame to compute linear segments based on frequency and flux values, ensuring sweep uniqueness.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with sweep, frequency, and flux columns.
    time : str, optional
        Column name representing time values. Default is 'Date_UTC'.
    frequency : str, optional
        Column name representing frequency values. Default is 'FREQ'.
    sweep : str, optional
        Column name representing sweep identifiers. Default is 'SWEEP'.
    flux : str, optional
        Column name representing flux values. Default is 'AMPL_Z'.
    preserve_cols : list, optional
        Columns to preserve in the final DataFrame. Default is ['DATETIME_Z', 'sweep_start_date'].
    preserve_funcs : list, optional
        Aggregation functions to apply to preserved columns. Default is ['min', 'max', 'median'].
    preserve_col_suffix : list, optional
        Suffixes for preserved column names. Default is an empty list.

    Returns
    -------
    pd.DataFrame
        Processed DataFrame with computed linear segments and/or preserved columns.
    
    Example
    -------
    >>> linear_segments(data, preserve_cols=['Date_UTC'], time='Date_UTC', frequency='freq', sweep='SWEEP', flux='akr_flux_si_1au')
    """
    # Check if the first sweep spans more than 10 minutes
    if (df.loc[df[sweep] == df[sweep].min(), [time]].max() -
        df.loc[df[sweep] == df[sweep].min(), [time]].min()).values[0] > np.timedelta64(10, 'm'):
        raise ValueError('Sweep number duplication covering more than 10 minutes')
    
    # Group by sweep and frequency, computing mean flux
    df_sweep_resampled = df.groupby([sweep, frequency])[flux].mean().reset_index()
    
    # Apply the fit_pandas function to compute linear segments
    fit_results = df_sweep_resampled.groupby(sweep, group_keys=False)[[sweep, frequency, flux]]\
        .apply(fit_pandas, sweep=sweep, frequency=frequency, flux=flux).reset_index(drop=True)
    
    if len(preserve_cols):  # If there are columns to preserve
        if not len(preserve_funcs):  # Ensure preservation functions are provided
            raise ValueError(f'No preservation functions. To preserve columns: {preserve_cols}, '
                             'functions are needed to describe how to preserve the columns')
        
        if not len(preserve_col_suffix):  # Assign suffixes based on function names if not provided
            preserve_col_suffix = [str(func) for func in preserve_funcs]
        
        g = df.groupby([sweep])[preserve_cols]  # Group by sweep for aggregation
        preserved = g.agg(preserve_funcs)  # Apply aggregation functions
        preserved.columns = [f"{col}_{stat}" for col, stat in preserved.columns]  # Rename columns
        preserved.reset_index(drop=False, inplace=True)  # Reset index to merge
        
        return fit_results.merge(preserved, on=sweep)  # Merge results with preserved data
    return fit_results

def process_in_chunks(hdf5_file, output_file, chunk_size=100):
    """
    Loads and processes HDF5 data in chunks while ensuring complete sweeps.
    The processed chunks are appended to an output HDF5 file.

    Parameters
    ----------
    hdf5_file : str
        Path to input HDF5 file.
    output_file : str
        Path to output HDF5 file.
    chunk_size : int, optional
        Number of sweeps to process in each chunk. Default is 100.

    Returns
    -------
    string
        path to output file.

    Example
    -------
    >>> process_in_chunks('input.h5', 'output.h5', chunk_size=50)
    """
    # Imports progressbar if available if not creates a dummy function
    try:
        from progressbar import progressbar
    except ImportError:
        def progressbar(*args, **kwargs):
            return args[0]
    
    # Open HDF5 file and retrieve unique sweep values
    with pd.HDFStore(hdf5_file, mode='r') as store:
        unique_sweeps = pd.read_hdf(store, key='main', columns=['SWEEP']).SWEEP.unique()
    
    # Loop through sweeps in chunks
    for i in progressbar(range(0, len(unique_sweeps), chunk_size), prefix='Looping SWEEP chunks: '):
        x1 = unique_sweeps[i]  # Start of chunk
        x2 = unique_sweeps[min(i + chunk_size - 1, len(unique_sweeps) - 1)]  # End of chunk
        
        # Load the relevant sweep data for the chunk
        chunk_data = pd.read_hdf(hdf5_file, where=f'SWEEP >= {x1} & SWEEP <= {x2}')
        
        # Process the chunk using linear segment fitting
        chunk_result = linear_segments(chunk_data, preserve_cols=['Date_UTC'], time='Date_UTC', flux='akr_flux_si_1au')
        
        # Append the processed chunk to the output HDF5 file
        chunk_result.to_hdf(output_file, key='processed', format='t', append=True, mode='a', data_columns=True)
    
        return output_file

    
def integrate_linear_segment(row, f_min=40, f_max=1040):
    """
    Computes the definite integral of a linear segment within specified frequency limits.

    Parameters
    ----------
    row : pd.Series
        A row containing the segment's slope, intercept, and frequency boundaries.
    f_min : float, optional
        The lower limit of integration. Default is 40.
    f_max : float, optional
        The upper limit of integration. Default is 1040.

    Returns
    -------
    float
        The computed integral value for the segment.

    Example
    -------
    >>> row = pd.Series({'slope': 2, 'intercept': 1, 'f1': 50, 'f2': 100})
    >>> integrate_linear_segment(row)
    6375.0
    """
    m = row['slope']  # Extract the slope of the segment
    c = row['intercept']  # Extract the intercept
    f1, f2 = row['f1'], row['f2']  # Extract segment frequency boundaries
    
    f_int_min = max(f1, f_min)  # Determine the lower bound for integration
    f_int_max = min(f2, f_max)  # Determine the upper bound for integration
    
    if f_int_min >= f_int_max:  # Check if the segment is outside the integration range
        return 0
    
    # Compute the definite integral of the linear function over the segment
    integral = (m / 2) * (f_int_max**2 - f_int_min**2) + c * (f_int_max - f_int_min)
    return integral

def integrate_with_variable_limits(row, f_min, f_max):
    """
    Computes the definite integral of a linear segment with variable frequency limits.

    Parameters
    ----------
    row : pd.Series
        A row containing the segment's slope, intercept, and frequency boundaries.
    f_min : dict
        A dictionary mapping sweep identifiers to minimum frequency values.
    f_max : dict
        A dictionary mapping sweep identifiers to maximum frequency values.

    Returns
    -------
    float
        The computed integral value for the segment.

    Example
    -------
    >>> row = pd.Series({'slope': 2, 'intercept': 1, 'f1': 50, 'f2': 100, 'SWEEP': 1})
    >>> f_min = {1: 40}
    >>> f_max = {1: 90}
    >>> integrate_with_variable_limits(row, f_min, f_max)
    4450.0
    """
    m = row['slope']  # Extract the slope
    c = row['intercept']  # Extract the intercept
    f1, f2 = row['f1'], row['f2']  # Extract segment frequency boundaries
    sweep = row['SWEEP']  # Extract the sweep identifier
    
    f_int_min = np.max([f1, f_min.get(sweep, np.nan)])  # Get the lower integration limit
    f_int_max = np.min([f2, f_max.get(sweep, np.nan)])  # Get the upper integration limit
    
    if np.isnan(f_int_min):  # Handle missing frequency limits
        return np.nan
    if f_int_min >= f_int_max:  # Check if the segment is outside the integration range
        return 0
    
    # Compute the definite integral
    integral = (m / 2) * (f_int_max**2 - f_int_min**2) + c * (f_int_max - f_int_min)
    return integral

def sum_ints(x, dist=1.496e11):
    """
    Computes the sum of a series, ignoring NaN values.

    Parameters
    ----------
    x : pd.Series
        The series to sum.

    Returns
    -------
    float
        The sum of non-NaN values.

    Example
    -------
    >>> sum_ints(pd.Series([1, 2, np.nan, 4]))
    7.0
    """
    return np.nansum(x.values)*(dist**2)*1e3

def integrate(df, flimits, sweep='SWEEP', fmin='fmin', fmax='fmax', distance=1.496e11):
    """
    Computes the total integral per sweep, using either fixed or variable limits.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the segment data.
    flimits : tuple or pd.DataFrame
        If a tuple, contains (fmin, fmax) fixed limits. If a DataFrame, provides per-sweep limits.
    sweep : str, optional
        Column name representing sweep identifiers. Default is 'SWEEP'.
    fmin : str, optional
        Column name representing the lower frequency limit. Default is 'fmin'. Not required if flimits is tuple.
    fmax : str, optional
        Column name representing the upper frequency limit. Default is 'fmax'. Not required if flimits is tuple.

    Returns
    -------
    pd.DataFrame
        DataFrame with integrated values per sweep.

    Example
    -------
    >>> df = pd.DataFrame({
    ...     'SWEEP': [1, 1, 2, 2],
    ...     'slope': [2, 2, 3, 3],
    ...     'intercept': [1, 1, 0, 0],
    ...     'f1': [50, 100, 200, 300],
    ...     'f2': [100, 150, 250, 350]
    ... })
    >>> flimits = (40, 140)
    >>> integrate(df, flimits)
       SWEEP  integral_40_140
    0      1           14850.0
    1      2           24000.0
    """
    df = df.copy()  # Create a copy of the DataFrame to avoid modifying the original
    
    if isinstance(flimits, pd.DataFrame):  # Check if flimits is a DataFrame
        fmin = dict(zip(flimits[sweep], flimits[fmin]))  # Convert fmin column to dictionary
        fmax = dict(zip(flimits[sweep], flimits[fmax]))  # Convert fmax column to dictionary
        df['integral_variable_limits'] = df.apply(integrate_with_variable_limits, axis=1, f_min=fmin, f_max=fmax)
        return df.groupby('SWEEP')['integral_variable_limits'].apply(lambda x: sum_ints(x, distance)).reset_index()
    else:
        fmin, fmax = flimits  # Extract fixed frequency limits
        df[f'integral_{fmin}_{fmax}'] = df.apply(integrate_linear_segment, axis=1, f_min=fmin, f_max=fmax)
        return df.groupby('SWEEP')[f'integral_{fmin}_{fmax}'].apply(lambda x: sum_ints(x, distance)).reset_index()
        
def create_sweeps(data, time='datetime_ut', sweep='SWEEP', inplace=True):
    """
    Assigns unique sweep numbers to data based on time factorization.

    Parameters
    ----------
    data : pd.DataFrame
        The input DataFrame containing time values.
    time : str, optional
        Column name representing time values. Default is 'datetime_ut'.
    sweep : str, optional
        Column name to store the generated sweep identifiers. Default is 'SWEEP'.
    inplace : bool, optional
        If True, modifies the input DataFrame in place. If False, returns a modified copy. Default is True.

    Returns
    -------
    pd.DataFrame or None
        If inplace is False, returns a modified DataFrame with the assigned sweep numbers.
        If inplace is True, modifies the DataFrame directly and returns None.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'datetime_ut': ['2024-03-01 00:00:00', '2024-03-01 00:01:00', '2024-03-01 00:01:00',
    ...                     '2024-03-01 00:02:00', '2024-03-01 00:03:00', '2024-03-01 00:03:00']
    ... })
    >>> df['datetime_ut'] = pd.to_datetime(df['datetime_ut'])
    >>> create_sweeps(df)
    >>> print(df)
             datetime_ut  SWEEP
    0 2024-03-01 00:00:00      1
    1 2024-03-01 00:01:00      2
    2 2024-03-01 00:01:00      2
    3 2024-03-01 00:02:00      3
    4 2024-03-01 00:03:00      4
    5 2024-03-01 00:03:00      4
    """
    if not inplace:  # If inplace is False, create a copy to avoid modifying the original DataFrame
        data = data.copy()
    
    data[sweep] = data[time].factorize()[0] + 1  # Assign unique sweep numbers based on factorized time values
    
    if not inplace:  # If inplace is False, return the modified DataFrame
        return data
if __name__=='__main__':
    file= 'wi_wa_rad1_l3_akr_20030101_v01.csv'
    df= pd.read_csv(file, parse_dates=['datetime_ut'])
    # -1 represents nan values
    df.replace(-1, np.nan, inplace=True)
    # Creating unique sweeps for each unique datetime
    create_sweeps(df, time='datetime_ut', inplace=True)
    # Linear Interpolation between frequencies
    df_lin= linear_segments(df, time='datetime_ut', frequency='freq', flux='akr_flux_si_1au', preserve_cols=['datetime_ut'])
    # Integrate across fix limits
    df_int1= integrate(df_lin, flimits=(20, 1000))
    # Creating variable flims
    sweeps= np.unique(df.SWEEP)
    freqs= np.unique(df.freq)
    flims= np.random.choice(freqs, (len(sweeps), 2))
    f_min, f_max= np.min(flims, axis=1), np.max(flims, axis=1)
    flims= pd.DataFrame({'fmin':f_min, 'fmax':f_max, 'SWEEP':sweeps})
    # Integrate aross variable limits
    df_int2= integrate(df_lin, flimits=flims, sweep='SWEEP', fmin='fmin', fmax='fmax')
    df_int2= df_int2.merge(flims, on='SWEEP')
