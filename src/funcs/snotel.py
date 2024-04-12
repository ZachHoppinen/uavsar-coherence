def clean_snotel(df):
    for col in ['SWE', 'SNOWDEPTH', 'AVG AIR TEMP']: df[col] = df[col].astype(float)
    # convert inches to meters
    df['swe'] = df['SWE'] * 0.0254
    df['sd'] = df['SNOWDEPTH'] * 0.0254
    # convert F to C
    df['temp'] = (df['AVG AIR TEMP'] - 32) * 5/9
    df = df.drop(['SWE', 'SWE_units', 'SNOWDEPTH', 'SNOWDEPTH_units', 'AVG AIR TEMP', 'AVG AIR TEMP_units'], axis = 1)
    return df