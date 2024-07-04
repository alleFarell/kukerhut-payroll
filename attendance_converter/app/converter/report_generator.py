# app/converter/report_generator.py

import pandas as pd
from .overtime_calculator import calculate_overtime, datetime_to_string
from .config import thresholds

def generate_report(df_complete, gaji_url):
    df_gaji = pd.read_csv(gaji_url)

    df_in = df_complete[df_complete['clocking_type'] == 0]
    df_out = df_complete[df_complete['clocking_type'] == 1]

    df_in = df_in.drop_duplicates(subset=['person_id', 'clocking_type', 'clock_date'], keep='first')
    df_out = df_out.drop_duplicates(subset=['person_id', 'clocking_type', 'clock_date'], keep='last')

    a = df_in[['person_id', 'clock_datetime', 'clock_date']]
    b = df_out[['person_id', 'clock_datetime', 'clock_date']]
    df_final = pd.merge(a, b, on=['person_id', 'clock_date'], how='left', suffixes=('_in', '_out'))
    df_final = df_final[['person_id', 'clock_date', 'clock_datetime_in', 'clock_datetime_out']]
    df_final['work_hour'] = df_final['clock_datetime_out'] - df_final['clock_datetime_in']

    df_final['overtime'] = df_final.apply(
        lambda row: row['work_hour'] - thresholds.get(row['person_id'], row['work_hour']) if row['work_hour'] > thresholds.get(row['person_id'], row['work_hour']) else pd.Timedelta(0),
        axis=1
    )

    calculate_overtime(df_final)
    datetime_to_string(df_final)

    df_final = pd.merge(left=df_final, right=df_gaji[['NO', 'NAMA']], left_on='person_id', right_on='NO', how='left')

    nama_to_person_id = df_final[['NAMA', 'person_id']].drop_duplicates()
    nama_to_person_id = nama_to_person_id.set_index('NAMA')['person_id'].to_dict()

    sorted_namas = sorted(nama_to_person_id, key=nama_to_person_id.get)

    df_pivot_table = df_final.pivot(index='clock_date', columns='NAMA', values=['clock_datetime_in', 'clock_datetime_out', 'work_hour_str', 'overtime_str', 'overtime_num'])

  # Ensure unique column names
    # df_pivot_table.columns = ['_'.join(col).strip() for col in df_pivot_table.columns.values]

    df_pivot_table = df_pivot_table.reindex(columns=sorted_namas, level=1)
    df_pivot_table = df_pivot_table.swaplevel(0, 1, axis=1).sort_index(level=0, axis=1)
    df_pivot_table = df_pivot_table.reindex(columns=sorted_namas, level=0)

    return df_pivot_table
