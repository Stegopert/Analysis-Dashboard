import numpy as np
#calculate rh in watervapour mixing ratio
#no for loop becaus run with loding
def rh_to_mixing_ratio(obs_df):
    obs_df['e'] = (obs_df['rf']/100)*6.112* np.exp((17.67 * obs_df['Temperature [°C]'])/(obs_df['Temperature [°C]'] + 243.5))
    obs_df['Water Vapor Mixing Ratio [g/kg]'] = (0.622 * obs_df['e'])*1000/(obs_df['Pressure [hPa]'] - obs_df['e'])
    return obs_df


def mixing_ratio_to_rh(model_df):
    # Convert mixing ratio from g/kg to kg/kg if needed (assuming it's given in g/kg in this case)
    model_df['e'] = (model_df['Q2'] / 1000) * model_df['PSFC'] / (0.622 + (model_df['Q2'] / 1000))
    # Calculate saturation vapor pressure at the given temperature
    model_df['es'] = 6.112 * np.exp((17.67 * model_df['T2']) / (model_df['T2'] + 243.5))
    # Calculate relative humidity as the ratio of actual vapor pressure to saturation vapor pressure
    model_df['rf'] = (model_df['e'] / model_df['es']) * 100
    return model_df



