# app/converter/overtime_calculator.py

import pandas as pd
import datetime as dt
from .config import thresholds, list_1

def is_overtime(person_id, work_hour):
    th = thresholds.get(person_id)
    return True if (work_hour > th) else False

def calculate_overtime(df):
    ls_ovt = []
    for i in range(len(df)):
        person_id = df['person_id'][i]
        work_hour = df['work_hour'][i]
        if is_overtime(person_id, work_hour):
            wh = divmod(work_hour.total_seconds(), 60)[0]
            if person_id in list_1:
                ovt = (wh - 600)
            else:
                ovt = (wh - 540)

            delta_ovt = divmod(ovt, 60)
            if delta_ovt[1] >= 30:
                ls_ovt.append(delta_ovt[0] + 1)
            else:
                ls_ovt.append(delta_ovt[0])
        else:
            ls_ovt.append(0)

    df['overtime_num'] = ls_ovt

def datetime_to_string(df):
    str_wh = []
    str_ovt = []
    for i in range(len(df)):
        if pd.isnull(df['work_hour'][i]):
            wh = pd.NaT
            ovt = pd.NaT
        else:
            value_wh = df['work_hour'][i]
            value_ovt = df['overtime'][i]

            wh = (dt.datetime.min + value_wh).time()
            ovt = (dt.datetime.min + value_ovt).time()

        str_wh.append(wh)
        str_ovt.append(ovt)

    df['work_hour_str'] = str_wh
    df['overtime_str'] = str_ovt
