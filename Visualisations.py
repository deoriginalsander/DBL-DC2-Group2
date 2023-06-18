import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns  # also improves the look of plots
from scipy.stats import *

import sqlite3

conn = sqlite3.connect('C:\database.db')
c = conn.cursor()
conn.commit()
#conn.close()

year_data = pd.DataFrame({'2010': [366,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan], '2011': [475,400,405,407,428,403,372,350,303,383,426,437],
                          '2012': [435,417,428,304,341,431,332,396,341,455,529,372],
                          '2013': [454,394,391,359,332,266,298,270,295,331,389,440],
                          '2014': [308,287,331,314,255,226,260,273,291,314,360,313],
                          '2015': [359,302,336,281,299,254,251,245,286,365,433,338],
                          '2016': [373,322,309,227,262,240,228,302,212,227,346,279],
                          '2017': [289,275,346,255,218,240,282,304,257,301,387,317],
                          '2018': [321,288,314,312,298,266,271,270,239,364,373,292],
                          '2019': [310,333,327,281,291,279,276,224,269,269,309,336],
                          '2020': [277,277,255,126,158,166,185,238,250,297,297,210],
                          '2021': [189,180,266,203,147,182,151,164,175,212,217,198],
                          '2022': [239,199,218,171,216,193,187,165,185,242,244,227],
                          '2023': [238,195,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]})



year_mean = year_data.mean()
df_year_mean = year_mean.to_frame()
year_data


year_average = df_year_mean.plot( kind="bar")
year_average.set_xticklabels(labels=['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023'], rotation = 45)
year_average.set_ylabel('Number of Burglaries')
year_average.set_xlabel('Year')
year_average.set_title('Yearly average of Burglaries in Barnet, UK', size=16, weight='bold');
year_average.legend(['Burglaries']);


year_average


year_data = pd.DataFrame({'2021': [np.nan,np.nan,266,203,147,182,151,164,175,212,217,198],
                          '2022': [239,199,218,171,216,193,187,165,185,242,244,227],
                          '2023': [238,195,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]})

jan_avg = year_data.loc[0].mean()
feb_avg = year_data.loc[1].mean()
mar_avg = year_data.loc[2].mean()
apr_avg = year_data.loc[3].mean()
may_avg = year_data.loc[4].mean()
jun_avg = year_data.loc[5].mean()
jul_avg = year_data.loc[6].mean()
aug_avg = year_data.loc[7].mean()
sep_avg = year_data.loc[8].mean()
oct_avg = year_data.loc[9].mean()
nov_avg = year_data.loc[10].mean()
dec_avg = year_data.loc[11].mean()

year_data = pd.DataFrame({'Average': [jan_avg, feb_avg, mar_avg, apr_avg, may_avg, jun_avg, jul_avg ,aug_avg, sep_avg, oct_avg, nov_avg, dec_avg],
                          '2021': [np.nan,np.nan,266,203,147,182,151,164,175,212,217,198],
                          '2022': [239,199,218,171,216,193,187,165,185,242,244,227],
                          '2023': [238,195,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]})

year_data

average_per_month = year_data.plot(y='Average', kind="bar", legend = False)
average_per_month.set_ylabel('Burglaries reported')
average_per_month.set_xlabel('Month')
average_per_month.set_xticklabels(labels=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], rotation = 45)
average_per_month.set_title('Average number of burglaries committed per month from Mar 2021 to Feb 2023 in Barnet, UK', size=16, weight='bold');
#average_per_month.legend(['Burglaries']);

plt.show()