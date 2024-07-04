# app/converter/config.py

import pandas as pd

# Define lists for different person IDs (Karyawan sif dan non sif)
list_1 = [3, 4, 6, 13, 20, 21, 25, 26]  # non shift
list_2 = [16, 17, 19, 22, 23, 24, 27, 28]  # shift

# list_1 = [3, 4, 6, 13, 20, 21]
# list_2 = [16, 17, 19, 22, 23]

# Define thresholds based on person ID lists
thresholds = {person_id: pd.Timedelta(hours=10) for person_id in list_1}
thresholds.update({person_id: pd.Timedelta(hours=9) for person_id in list_2})

year_filter = 2024
month_filter = 5
