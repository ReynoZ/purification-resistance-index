# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 15:37:12 2023

@author: ZhangXY
"""
# =============================================================================
# This file contains code to calculate each sub-index.
# =============================================================================
import numpy as np
import pandas as pd


# Check if all status parameters are not less than 0
def gamma_input_valid_check(tau, chla, T, pH):
    params = [tau, chla, T, pH]
    flag = 0
    for param in params:
        if param < 0:
            flag = 1
            break
    return flag


# Calculate the weights given data (e.g. reduction rate)
def weight_calc_1(data):
    weights = (1 - data) / (1 - data).sum()
    return weights


def weight_calc_2(data):
    weights = data / data.sum()
    return weights


# Calculate each part of gamma
def get_tau(tau):
    if 0 <= tau <= 1:
        y = np.log(40)
    elif tau >= 40:
        y = 0
    elif 1 < tau < 40:
        y = np.log(40 / tau)
    else:
        raise ValueError("Unable to calculate r_c due to negative status parameter tau.")
    return y


def get_chla(chla):
    y = chla / 26
    return y


def get_t(T):
    y = 1 - 0.2 * T ** 0.45
    return y


def get_ph(pH):
    if 6 <= pH <= 9:
        return 0
    else:
        return 1


# Main function to calc r_c
def calc_coagulation(p_status, p_in, printOrnot=False, weighing_option=1):
    # Read in the limitation file to know the limitations for each parameter
    lim = pd.read_csv(r'ref_data\lim_1.csv', index_col=0)
    tau, chla, T, pH = p_status  # unpack the status parameters
    if gamma_input_valid_check(tau, chla, T, pH):
        raise ValueError("Unable to calculate r_c due to negative status parameter value(s).")
    # Calculate the coagulation resistance coefficient, gamma
    gamma = get_tau(tau) + get_chla(chla) + get_t(T) + get_ph(pH)
    # Calculate weights for each parameter
    re_rate = lim['reduction rate'][1:]
    weights = np.array(weight_calc_1(re_rate))
    p_out = lim['Value'][1:]  # effluent limitations for each parameter
    exceeds = np.array(p_in / p_out)

    # Calculate the coagulation resistance, r_c with unequal weights
    output = gamma * (weighing_option * tau + np.nansum(exceeds * weights))

    if printOrnot:
        print(gamma, weights, exceeds, output)
    return output


def kow():
    logKows = pd.read_csv(r'ref_data\logKow.csv', index_col=0)
    logKows['Value'] = 10 ** logKows['Value']
    vphenols = logKows[:14]['Value']
    las = logKows[14:15]['Value']
    petrol = logKows[15:]['Value']
    w_1 = (np.array(vphenols).flatten() * np.array(logKows[:14]['Weight'])).sum()
    w_2 = las.iloc[0]
    w_3 = (np.array(petrol).flatten() * np.array(logKows[15:]['Weight'])).sum()
    ws = np.array([1 / w_1, 1 / w_2, 1 / w_3])
    ws = np.array(list(map(np.log10, ws)))
    w0 = weight_calc_2(ws)
    swap = np.array([1 / w for w in w0])
    weights = weight_calc_2(swap)
    return weights


# Main function to calc r_f
def calc_filtration(tau, p_in, turbFactor=True, printOrnot=False, weighing_option=1):
    # Read in the limitation file to know the limitations for each parameter
    lim = pd.read_csv(r'ref_data\lim_2.csv', index_col=0)
    # Calculate weights for each parameter
    weights = kow()
    p_out = lim['Value']  # effluent limitations for each parameter
    exceeds = np.array(p_in / p_out)
    # Calculate the coagulation resistance, r_c
    if turbFactor:
        output = weighing_option * 0.1 * tau / 0.3 + np.nansum(exceeds * weights)
    else:
        output = np.nansum(exceeds * weights)
    if printOrnot:
        print(weights, exceeds, output)
    return output


# Main function to calc r_d
def calc_disinfection(p_in, printOrnot=False):
    # Read in the limitation file to know the limitations for each parameter
    lim = pd.read_csv(r'ref_data\lim_3.csv', index_col=0)
    cs = lim.iloc[0, 1]
    r = lim.iloc[2, 1]
    cts = lim.iloc[3, 1]
    # Unpack parameters and calculate CT value
    ce, ca, T = p_in
    ct = 12 * np.e ** (-0.072 * T)
    # Calculate the disinfection resistance, r_d
    output = (ce / cs + 7.16) * ca / r * (ct / cts)
    if printOrnot:
        print(ct, output)
    return output


# Main function to calc r_a
def calc_advanced(p_in):
    # Read in the limitation file to know the limitations for each parameter
    lim = pd.read_csv(r'ref_data\lim_4.csv', index_col=0)

    lim['delta'] = p_in - lim['Value']  # calculate delta
    exceed_paras = lim[lim['delta'] > 0][['Value', 'delta', 'Complexity']]  # select when delta more than 0
    exceed_paras['ratio'] = exceed_paras['delta'] / exceed_paras['Value'] + 1
    summary = exceed_paras.groupby('Complexity').sum()
    summary['r'] = summary['ratio'] * summary.index
    output = summary['r'].sum()
    return output


def ra_class(r_a):
    if r_a == 0:
        rtype = 'a'
    elif 1 <= r_a < 2:
        rtype = 'b'
    elif r_a >= 2:
        rtype = 'c'
    else:
        rtype = 'E'

    return rtype


# Only for testing
def test_coagulation_index():
    p_in = np.array([0.3, np.nan, 1.0, 0, 0])
    p_status = np.array([84, 43, 23, 7.6])

    resistance = calc_coagulation(p_status, p_in, printOrnot=True)
    print(resistance)


def test_filter_index():
    tau = 84
    p_in = np.array([0.05, 0.4, 0.05])

    resistance = calc_filtration(tau, p_in, printOrnot=True)
    print(resistance)


def test_disinfection_index():
    p_in = np.array([1400, 0.64, 23])

    resistance = calc_disinfection(p_in, printOrnot=True)
    print(resistance)


def test_advanced_index():
    p_in = np.array([5, np.nan, 0.3, 0.05, 0, 0.002, 1, 0, 0.000012, 2, 152, 200])

    resistance = calc_advanced(p_in)
    print(resistance)
