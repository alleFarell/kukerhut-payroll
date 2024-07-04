# app/converter/data_processing.py

import pandas as pd
import datetime as dt
# from .config import year_filter, month_filter

def load_data(file_path):
    df_raw = pd.read_fwf(file_path,
                         header=None,
                         names=["person_id", "clock_date", "clock_time", "device_id", "clocking_type", "unused_1", "unused_2"])
    df_raw = df_raw.drop(columns=["device_id", "unused_1", "unused_2"])
    df_raw["clock_datetime"] = pd.to_datetime(df_raw['clock_date'] + " " + df_raw["clock_time"], format='%Y-%m-%d %H:%M:%S')
    df_raw['clock_date'] = pd.to_datetime(df_raw['clock_date'], format='%Y-%m-%d')
    df_raw = df_raw[['person_id', 'clock_datetime', 'clocking_type', 'clock_date']]
    return df_raw

def clean_filter_data(file_path, year, month):
    df_raw = load_data(file_path)
    df_filtered = df_raw[(df_raw["clock_datetime"].dt.month == month) &
                         (df_raw["clock_datetime"].dt.year == year)]

    # Replace clocking type 4 to 0 or 1 based on clock_time
    cek_masuk = dt.datetime.strptime('08:30:00', '%H:%M:%S')
    cek_pulang = dt.datetime.strptime('15:00:00', '%H:%M:%S')

    df_filtered.loc[(df_filtered["clocking_type"] == 4) & (df_filtered['clock_datetime'].dt.time < cek_pulang.time()), 'clocking_type'] = 0
    df_filtered.loc[(df_filtered["clocking_type"] == 4) & (df_filtered['clock_datetime'].dt.time > cek_pulang.time()), 'clocking_type'] = 1

    # False IN validation
    df_filtered.loc[(df_filtered['clock_datetime'].dt.time > cek_pulang.time()) &
                    (df_filtered['clocking_type'] == 0), 'clocking_type'] = 1

    # False OUT validation
    df_filtered.loc[(df_filtered['clock_datetime'].dt.time < cek_masuk.time()) &
                    (df_filtered['clocking_type'] == 1), 'clocking_type'] = 0

    # Sort data by person_id, clocking_type, clock_datetime
    df_clean = df_filtered.sort_values(by=['person_id', 'clocking_type', 'clock_datetime'], ignore_index=True)
    return df_clean

def merge_datasets(df1, df2):
    df_complete = pd.concat([df1, df2], axis=0, ignore_index=True)
    df_complete = df_complete.sort_values(by=['person_id', 'clocking_type', 'clock_datetime'], ignore_index=True)
    return df_complete
