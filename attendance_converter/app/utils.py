import pandas as pd

def read_dat_file(file_path):
    """
    Reads a .dat file and returns a DataFrame with clock-in and clock-out data.
    """
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 3:
                employee_id, timestamp, action = parts
                data.append({'employee_id': employee_id, 'timestamp': timestamp, 'action': action})
    return pd.DataFrame(data)


def generate_excel_report(dataframe, output_path):
    """
    Generates an Excel report from the DataFrame.
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Attendance')
