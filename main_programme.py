# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 17:13:49 2023

@author: Xiaoyu Zhang, rong he, jiping jiang
@Instituion: sustech.
Reference：jiang, Zhang, ........
contact:XXx ;jjp_lab@sina.com
@copy non-common 
"""

# =============================================================================
# This is the main programme to calculate the PRI
# =============================================================================

import numpy as np
import pandas as pd
from calc_subindex import calc_coagulation, calc_filtration, calc_disinfection, calc_advanced, ra_class


# Function to replace "L" with 0 in a cell
def replace_L_with_0(cell_value):
    if isinstance(cell_value, str) and 'L' in cell_value:
        return cell_value.replace('L', '0')
    return cell_value


def data_input(input_path=r'Input\demo.csv'):
    # Read in the data and select specific paras and delete the empty rows

    df = pd.read_csv(input_path, encoding='gbk')
    col_names = ['Sites', 'Date', 'W_temp', 'pH', 'CODMn', 'NH4-N', 'F', 'As', 'Cd',
                 'Cn_total', 'V_phen', 'Oils', 'An_SAA', 'Colo_org', 'SO4', 'Cl',
                 'NO3_n', 'W_Fe', 'W_Mn', 'Transp', 'Chl_a']
    df.columns = col_names

    # Apply the function to specific columns (e.g., only numeric columns)
    columns_to_replace = df.columns[3:]

    # Apply the function to the specified columns
    df[columns_to_replace] = df[columns_to_replace].map(replace_L_with_0)
    df[columns_to_replace] = df[columns_to_replace].map(pd.to_numeric, errors='coerce')

    # Replace value -1 with nan
    df = df.replace(-1, np.nan)

    # Convert Transp (cm) to Turbidity (NTU)
    df['Turbid'] = 4686 * df['Transp'] ** (-1.532)

    # Create a 'Warning' column with an initial value of 'Pass'
    df['Warning'] = 'Pass'

    return df


def get_input(x, i, df):
    # Get input parameter values
    para_names = list(pd.read_csv(rf'ref_data\lim_{x}.csv', index_col=0).index)
    # Check for missing parameters
    missing_parameters = [param for param in para_names if param not in df.columns]
    new_list = [param for param in para_names if param in df.columns]

    if missing_parameters:
        p_in = df[new_list].iloc[i]
    else:
        p_in = df[para_names].iloc[i]
    return p_in


def start_calc(input_path, out_path):
    df = data_input(input_path)

    PRI_cols = ['PRI_c', 'PRI_f', 'PRI_d', 'PRI_a', 'Type', 'PRI']
    df[PRI_cols] = None  # initialize the new columns with None

    vital_paras = ['Turbid', 'W_temp', 'pH', 'Colo_org', 'NH4-N', 'CODMn']

    for i in range(len(df)):  # iterate every row
        # Validation check
        if df.loc[i, vital_paras].isna().any():
            df.loc[i, 'Warning'] = 'Fail'
            continue
        # Calculate coagulation resistance sub-index
        p_status = df[['Turbid', 'Chl_a', 'W_temp', 'pH']].iloc[i]  # get status paras
        c_p_in = get_input(1, i, df)  # get input para values
        r_c = calc_coagulation(p_status, c_p_in[1:])  # calc r_c
        # Calculate filtration resistance sub-index
        tau = p_status.iloc[0]
        f_p_in = get_input(2, i, df)  # get input para values
        r_f = calc_filtration(tau, f_p_in)  # calc r_f
        # Calculate disinfection resistance sub-index
        d_p_in = df[['Colo_org', 'NH4-N', 'W_temp']].iloc[i]  # get input para values
        r_d = calc_disinfection(d_p_in)  # calc r_d
        # Calculate advanced resistance sub-index
        a_p_in = get_input(4, i, df)  # get input para values
        r_a = calc_advanced(a_p_in)  # calc r_a

        r_sum = r_c + r_f + r_d  # sum up the sub-indices
        ratype = ra_class(r_a)  # class a or b or c?

        pri = str(round(r_sum, 2)) + ratype  # dual-index

        df.loc[i, PRI_cols] = [r_c, r_f, r_d, r_a, ratype, pri]

    print("Calculation Completed")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print("Output Completed")

    return df


if __name__ == '__main__':
    input_file = r'.\Input\demo.csv'
    out_file = r'.\Output\PRIoutput.csv'
    start_calc(input_file, out_file)
