import pandas as pd
import numpy as np

from scipy.stats import gamma


def get_covid_data():
    confirmed_data = pd.read_csv(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")

    confirmed_data = (confirmed_data.groupby(
        "Country/Region").sum()).drop(columns=['Lat', 'Long'])
    confirmed_data = confirmed_data.drop(['Diamond Princess','MS Zaandam'])

    data_dates = pd.to_datetime(confirmed_data.columns, format='%m/%d/%y')
    countries_list = list(confirmed_data.index)

    confirmed_data = np.array(confirmed_data)
    epicurves = get_epicurves(confirmed_data)
    rcurves = compute_dynamic_r(epicurves, data_dates, countries_list, 3)

    return confirmed_data, epicurves, rcurves, countries_list, data_dates


def get_epicurves(confirmed_data):
    epicurves = np.diff(confirmed_data, n=1, axis=1)
    epicurves[epicurves < 0] = 0  # cumulative sum cannot drop

    return epicurves


def all_nonzero_window_starts(epicurve, win_start, win_size):
    win_end = epicurve.shape[0]
    all_win_starts = list()
    for t in range(win_start,(win_end - win_size)+1):
        if np.sum(epicurve[t:t+win_size+1]) > 0:
            all_win_starts.append(t)
    return all_win_starts


def p_all_taus(epicurve, theta):
    n_observations = epicurve.shape[0]
    all_taus = np.subtract.outer(range(n_observations), range(n_observations))
    w_all_taus = gamma.pdf(all_taus, a=theta[0], scale=theta[1])
    sum_w_all_taus = np.sum(w_all_taus*epicurve.reshape(1,-1), axis=1)
    sum_w_all_taus_matrix = np.tile(sum_w_all_taus, reps=(epicurve.shape[0],1))
    sum_w_all_taus_matrix = np.transpose(sum_w_all_taus_matrix)

    p = np.true_divide(w_all_taus, sum_w_all_taus_matrix)
    p[np.isinf(p)] = 0.0
    p[np.isnan(p)] = 0.0
    return p


def mean_r_all_windows(epicurve, mean_r_per_day, win_starts, win_size):
    n_windows = len(win_starts)
    mean_r_per_window = np.zeros(n_windows, np.float32)
    for i in range(n_windows):
        idx = win_starts[i]
        idx_end = idx + win_size + 1
        mean_r_per_window[i] = np.sum((mean_r_per_day[idx:idx_end]*epicurve[idx:idx_end]))/np.sum(epicurve[idx:idx_end])
    return mean_r_per_window


def compute_dynamic_r(epicurves, epi_dates, countries_list, win_size):
    dynamic_r = dict() # keys are countries
    win_size = win_size

    # gamma serial interval distribution parameters
    theta = [1.46, 0.78]

    # for each region, assure at least one case exists before the window begins
    window_starts_per_region = np.argmax(epicurves>0, axis=1) + 1
    for idx in range(epicurves.shape[0]):
        region_dynamic_r = dict() # keys are 'dates', 'mean_r'

        epicurve = epicurves[idx]
        all_win_starts = all_nonzero_window_starts(epicurve,
                                                   window_starts_per_region[idx],
                                                   win_size = win_size)
        p = p_all_taus(epicurve, theta)
        mean_r_per_day = np.sum(p*epicurve.reshape(-1,1), axis=0)
        mean_r_per_window = mean_r_all_windows(epicurve, mean_r_per_day,
                                               all_win_starts, win_size)

        region_dynamic_r['dates'] = epi_dates[all_win_starts]
        region_dynamic_r['mean_r'] = mean_r_per_window.tolist()
        dynamic_r[countries_list[idx]] = region_dynamic_r

    return dynamic_r

def get_country_iso_codes():
    return {'Afghanistan': 'AFG',
 'Albania': 'ALB',
 'Algeria': 'DZA',
 'Andorra': 'AND',
 'Angola': 'AGO',
 'Antigua and Barbuda': 'ATG',
 'Argentina': 'ARG',
 'Armenia': 'ARM',
 'Australia': 'AUS',
 'Austria': 'AUT',
 'Azerbaijan': 'AZE',
 'Bahamas': 'BHS',
 'Bahrain': 'BHR',
 'Bangladesh': 'BGD',
 'Barbados': 'BRB',
 'Belarus': 'BLR',
 'Belgium': 'BEL',
 'Belize': 'BLZ',
 'Benin': 'BEN',
 'Bhutan': 'BTN',
 'Bolivia': 'BOL',
 'Bosnia and Herzegovina': 'BIH',
 'Brazil': 'BRA',
 'Brunei': 'BRN',
 'Bulgaria': 'BGR',
 'Burkina Faso': 'BFA',
 'Burma': 'MMR',
 'Cabo Verde': 'CPV',
 'Cambodia': 'KHM',
 'Cameroon': 'CMR',
 'Canada': 'CAN',
 'Central African Republic': 'CAF',
 'Chad': 'TCD',
 'Chile': 'CHL',
 'China': 'CHN',
 'Colombia': 'COL',
 'Congo (Brazzaville)': 'COG',
 'Congo (Kinshasa)': 'COD',
 'Costa Rica': 'CRI',
 "Cote d'Ivoire": 'CIV',
 'Croatia': 'HRV',
 'Cuba': 'CUB',
 'Cyprus': 'CYP',
 'Czechia': 'CZE',
 'Denmark': 'DNK',
 'Djibouti': 'DJI',
 'Dominica': 'DMA',
 'Dominican Republic': 'DOM',
 'Ecuador': 'ECU',
 'Egypt': 'EGY',
 'El Salvador': 'SLV',
 'Equatorial Guinea': 'GNQ',
 'Eritrea': 'ERI',
 'Estonia': 'EST',
 'Eswatini': 'SWZ',
 'Ethiopia': 'ETH',
 'Fiji': 'FJI',
 'Finland': 'FIN',
 'France': 'FRA',
 'Gabon': 'GAB',
 'Gambia': 'GMB',
 'Georgia': 'GEO',
 'Germany': 'DEU',
 'Ghana': 'GHA',
 'Greece': 'GRC',
 'Grenada': 'GRD',
 'Guatemala': 'GTM',
 'Guinea': 'GIN',
 'Guinea-Bissau': 'GNB',
 'Guyana': 'GUY',
 'Haiti': 'HTI',
 'Holy See': 'VAT',
 'Honduras': 'HND',
 'Hungary': 'HUN',
 'Iceland': 'ISL',
 'India': 'IND',
 'Indonesia': 'IDN',
 'Iran': 'IRN',
 'Iraq': 'IRQ',
 'Ireland': 'IRL',
 'Israel': 'ISR',
 'Italy': 'ITA',
 'Jamaica': 'JAM',
 'Japan': 'JPN',
 'Jordan': 'JOR',
 'Kazakhstan': 'KAZ',
 'Kenya': 'KEN',
 'Korea, South': 'KOR',
 'Kosovo': 'KSO',
 'Kuwait': 'KWT',
 'Kyrgyzstan': 'KGZ',
 'Laos': 'LAO',
 'Latvia': 'LVA',
 'Lebanon': 'LBN',
 'Liberia': 'LBR',
 'Libya': 'LBY',
 'Liechtenstein': 'LIE',
 'Lithuania': 'LTU',
 'Luxembourg': 'LUX',
 'Madagascar': 'MDG',
 'Malaysia': 'MYS',
 'Maldives': 'MDV',
 'Mali': 'MLI',
 'Malta': 'MLT',
 'Mauritania': 'MRT',
 'Mauritius': 'MUS',
 'Mexico': 'MEX',
 'Moldova': 'MDA',
 'Monaco': 'MCO',
 'Mongolia': 'MNG',
 'Montenegro': 'MNE',
 'Morocco': 'MAR',
 'Mozambique': 'MOZ',
 'Namibia': 'NAM',
 'Nepal': 'NPL',
 'Netherlands': 'NLD',
 'New Zealand': 'NZL',
 'Nicaragua': 'NIC',
 'Niger': 'NER',
 'Nigeria': 'NGA',
 'North Macedonia': 'MKD',
 'Norway': 'NOR',
 'Oman': 'OMN',
 'Pakistan': 'PAK',
 'Panama': 'PAN',
 'Papua New Guinea': 'PNG',
 'Paraguay': 'PRY',
 'Peru': 'PER',
 'Philippines': 'PHL',
 'Poland': 'POL',
 'Portugal': 'PRT',
 'Qatar': 'QAT',
 'Romania': 'ROU',
 'Russia': 'RUS',
 'Rwanda': 'RWA',
 'Saint Kitts and Nevis': 'KNA',
 'Saint Lucia': 'LCA',
 'Saint Vincent and the Grenadines': 'VCT',
 'San Marino': 'SMR',
 'Saudi Arabia': 'SAU',
 'Senegal': 'SEN',
 'Serbia': 'SRB',
 'Seychelles': 'SYC',
 'Singapore': 'SGP',
 'Slovakia': 'SVK',
 'Slovenia': 'SVN',
 'Somalia': 'SOM',
 'South Africa': 'ZAF',
 'Spain': 'ESP',
 'Sri Lanka': 'LKA',
 'Sudan': 'SDN',
 'Suriname': 'SUR',
 'Sweden': 'SWE',
 'Switzerland': 'CHE',
 'Syria': 'SYR',
 'Taiwan*': 'TWN',
 'Tanzania': 'TZA',
 'Thailand': 'THA',
 'Timor-Leste': 'TLS',
 'Togo': 'TGO',
 'Trinidad and Tobago': 'TTO',
 'Tunisia': 'TUN',
 'Turkey': 'TUR',
 'US': 'USA',
 'Uganda': 'UGA',
 'Ukraine': 'UKR',
 'United Arab Emirates': 'ARE',
 'United Kingdom': 'GBR',
 'Uruguay': 'URY',
 'Uzbekistan': 'UZB',
 'Venezuela': 'VEN',
 'Vietnam': 'VNM',
 'West Bank and Gaza': 'PSE',
 'Zambia': 'ZMB',
 'Zimbabwe': 'ZWE'}
