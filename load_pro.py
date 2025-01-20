import os
import pandas as pd

folder_paths = ['Data/Models/BULK', 'Data/Models/SLUCM', 'Data/Models/BEP']

def load_model_data(folder_paths = folder_paths):
    # List of folder paths
    

    # Initialize a list to store metadata and data
    metadata = []
    data_frames = []

    
    for folder_path in folder_paths:
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):  
                # Extract metadata from the filename
                parts = os.path.splitext(filename)[0].split("_")

                #clean up the parts to only contain: case, LSM, UCM, and STATION
                while len(parts) > 4:
                    parts.pop(3)
                
                    
                if len(parts) == 4:  # Ensure the filename has the expected format
                    case, LSM, UCM, STATION = parts
                    file_path = os.path.join(folder_path, filename)
                        
                    # Read the CSV file into a DataFrame
                    df = pd.read_csv(file_path, parse_dates=['DateTime'])
                    df['DateTime'] = pd.to_datetime(df['DateTime'], utc=True)
                    df = df.set_index('DateTime')
                    # Add metadata as columns to the DataFrame
                    df['case'] = case
                    df['LSM'] = LSM
                    df['UCM'] = UCM
                    df['STATION'] = STATION
                    spinup_period = df.index[0] + pd.Timedelta(hours=12)
                    df = df[df.index > spinup_period]
                    df.set_index(["case", "LSM", "UCM", "STATION"], append=True, inplace=True)
                    df = df.reorder_levels(["case", "LSM", "UCM", "STATION", "DateTime"])
                    # Append metadata and DataFrame to their respective lists
                    metadata.append((case, LSM, UCM, STATION, file_path))
                    data_frames.append(df)
    
    # Combine all data into a single DataFrame
    data = pd.concat(data_frames)

    return data

def load_obs_data(folder_path='Data/Observations'):
    
    data_frames = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):  # Process only CSV files
            # Remove the file extension and split by "_"
            parts = os.path.splitext(filename)[0].split("_")

            #clean up the parts to only contain: case, LSM, UCM, and STATION
            while len(parts) > 3:
                parts.pop(2)
                
                    
            if len(parts) == 3:  # Ensure the filename has the expected format
                case, obs,STATION = parts
                file_path = os.path.join(folder_path, filename)
                        
                # Read the CSV file into a DataFrame
                df = pd.read_csv(file_path, parse_dates=['DateTime'])
                df['DateTime'] = pd.to_datetime(df['DateTime'], utc=True)
                df = df.set_index('DateTime')
                df.index = pd.to_datetime(df.index)
                #match model data
                df = df[df.index.minute.isin([0, 30])]

                df.rename(columns={ 
                    'tl': 'Temperature [°C]', 'rr': 'precipetation',
                    'p': 'Pressure [hPa]','pred': 'reduced pressure',
                    'ff': 'Windspeed [m/s]','dd': 'Winddirection [°]',
                    'so' : 'Sunshineduration', 'cglo': 'Globalradiation',
                    }, inplace=True)
                
                # delete spinup period of 12 hours
                spinup_period = df.index[0] + pd.Timedelta(hours=12)
                df = df[df.index > spinup_period]
                from calculations import rh_to_mixing_ratio
                # Calculate mixing ratio and add columns
                df = rh_to_mixing_ratio(df)
                df["case"] = case
                df["STATION"] = STATION
                df.set_index(["case", "STATION"], append=True, inplace=True)
                df = df.reorder_levels(["case", "STATION", "DateTime"])
                # Append metadata and DataFrame to their respective lists
                data_frames.append(df)
    
    # Combine all data into a single DataFrame
    data = pd.concat(data_frames)

    return data