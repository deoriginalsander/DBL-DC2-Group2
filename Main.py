import os
import sqlite3
import pandas as pd
import datetime
from datetime import date
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
from sklearn.cluster import KMeans
from matplotlib import cm
from pulp import *

conn = sqlite3.connect('C:\\database.db')
c = conn.cursor()


def make_db():
    c.execute("""CREATE TABLE accidents (
                                Crime_ID blob,
                                Month blob,
                                Reported_by blob,
                                Falls_within blob,
                                Longitude blob,
                                Latitude blob,
                                Location blob,
                                LSOA_code blob,
                                LSOA_name blob,
                                Crime_type blob,
                                Last_outcome_category blob,
                                Context blob)
                                """)


def load_data(directory):
    for folder in os.listdir(directory):
        print(folder)
        for file in os.listdir('E:\\data\\data\\' + folder):
            deletec_value = []
            data = pd.read_csv('E:\\data\\data\\' + folder + '\\' + file)
            for line in data.iterrows():
                values = ', '.join("'" + str(x).replace("'", "-") + "'" for x in line[1])
                data_line = values.split(',')
                if len(data_line) == 10:
                    data_line.append(data_line[9])
                    data_line[9] = ' NaN'
                    data_line.append(' NaN')
                    values = ', '.join("'" + str(x) + "'" for x in data_line)
                try:
                    c.execute(
                        'INSERT INTO accidents (Crime_ID, Month, Reported_by, Falls_within, Longitude, Latitude, Location, LSOA_code, LSOA_name, Crime_type, Last_outcome_category, Context) VALUES (' + values + ')')
                except:
                    deletec_value.append(values)
    print(deletec_value)


def clean_data():
    c.execute("""DELETE FROM accidents
                WHERE LSOA_name NOT LIKE '%Barnet%'
                """)
    c.execute("""DELETE FROM accidents
                WHERE Crime_type IS NOT 'Burglary'""")
    # c.execute("""ALTER TABLE accidents
    #                 DROP COLUMN Reported_by""")
    # c.execute("""ALTER TABLE accidents
    #                 DROP COLUMN context""")
    c.execute("""ALTER TABLE accidents
                    DROP COLUMN Falls_within""")
    c.execute("""ALTER TABLE accidents
                    DROP COLUMN Crime_ID""")
    c.execute("""ALTER TABLE accidents
                    DROP COLUMN LSOA_code""")
    c.execute("""ALTER TABLE accidents
                    DROP COLUMN Crime_type""")


def predict_burglary():
    per_month = c.execute("""SELECT COUNT(Latitude), month, LSOA_name
                        FROM accidents
                        GROUP BY month, LSOA_name""")
    df = pd.DataFrame(per_month, columns=['count', 'month', 'LSOA_name'])
    c.execute("""SELECT LSOA_name
                            FROM accidents
                            GROUP BY LSOA_name""")
    LSOA = c.fetchall()
    LSOA_list = [row[0] for row in LSOA]

    # getting inputs for determining the timeline
    date1 = date.today()
    month = int(input('Select month'))
    year = int(input('Select year'))
    mode = input('seasonal or Yearly average?')

    # checking if the asked month has already passed or is the next month.
    latest_month = df['month'][-1:].values[0]
    if month - int(latest_month[5:7]) > 1 and year >= int(latest_month[0:4]):
        print('There is not enough data to determine result')
        return

    # looping over the LSOA's to find the corresponding value for each of them and assigning a value to that LSOA
    LSOA_values = {}
    if len(str(month))==1:
        memory = ['0' + str(month), year]
    else:
        memory = [str(month), year]
    for item in LSOA_list:
        # defining needed vars
        month = int(memory[0])
        year = memory[1]
        score = 0
        monthly_ratios_1 = []
        monthly_ratios_2 = []
        weighted_list = [1, 0.7, 0.4, 0.3, 0.2]
        # getting data for that specific LSOA
        df2 = df[df['LSOA_name'] == item]

        # getting the values for the 5 months before hand
        for i in range(1, 6):
            month = int(month) - 1
            if month < 1:
                month += 12
                year -= 1
            if len(str(month)) == 1:
                month = '0' + str(month)

            # getting the values for this year
            current_year_df = df2[df2['month'] == (str(year) + '-' + str(month))]
            current_year_series = current_year_df['count'].values
            try:
                count_current_year = current_year_series[0]
            except:
                count_current_year = 0

            # getting values for previous year
            previous_year_df = df2[df2['month'] == (str(year - 1) + '-' + str(month))]
            previous_year_series = previous_year_df['count'].values
            try:
                real_previous_year = previous_year_series[0]
                count_previous_year = previous_year_series[0]
            except:
                real_previous_year = 0
                count_previous_year = 1

            # getting values 2 year before
            two_years_ago = df2[df2['month'] == (str(year - 2) + '-' + str(month))]
            two_year_ago_series = two_years_ago['count'].values
            try:
                count_two_year_ago = two_year_ago_series[0]
            except:
                count_two_year_ago = 1

            monthly_ratios_1.append(count_current_year / count_previous_year)
            monthly_ratios_2.append(count_current_year / count_two_year_ago)

        # computing average over last 12 months
        for year in range(2010, memory[1] - 1):
            df2 = df2.drop(list(df2[df2['month'].str.contains(str(year))].index))
        for months in range(1, int(memory[0]) + 1):
            if len(str(months)) == 1:
                remove_month = '0' + str(months)
            else:
                remove_month = str(months)
            df2 = df2.drop(list(df2[df2['month'] == str(memory[1] - 1) + '-' + remove_month].index))
        average_last_12_months = sum(df2['count']) / 12

        # computing the score
        end_list = []
        for i in range(0, 5):
            end_list.append((monthly_ratios_1[i] * 3 + monthly_ratios_2[i]) / 4 * weighted_list[i])
        # if len(str(memory[0]))==1:
        #     moth_selected = '0'+str(memory[0])
        last_year_current_month = df2[df2['month'] == (str(memory[1] - 1) + '-' + memory[0])]
        two_year_ago_current_month = df2[df2['month'] == (str(memory[1] - 2) + '-' + memory[0])]
        # rate_current_month_last_years = last_year_current_month[0][0]/two_year_ago_current_month[0][0]
        # print(str(memory[1]-1)+'-'+moth_selected)
        if mode == 'seasonal':
            try:
                score = sum(end_list) / 5 * last_year_current_month[0][0]
            except:
                score = sum(end_list) / 5

        else:
            score = sum(end_list) / 5 * average_last_12_months
        LSOA_values[item] = score
    print(LSOA_values)
    return (LSOA_values)

    list_of_patrols = []
    for i in range(0, 10):
        highest_count = max(LSOA_values.values())
        most_treat_LSOA = list(LSOA_values.keys())[list(LSOA_values.values()).index(highest_count)]
        list_of_patrols.append(most_treat_LSOA + ' ' + str(highest_count))
        LSOA_values.pop(most_treat_LSOA)

    high_risk = get_most_burglary_LSOA(memory[0], memory[1])
    for item in list_of_patrols:
        if item[:11] in high_risk:
            print(item[:11])
        else:
            print(item[:11] + ' nope')
    print(list_of_patrols)


def get_most_burglary_LSOA(month, year):
    target_month = str(year) + '-' + month
    per_month = c.execute("""SELECT COUNT(Latitude), month, LSOA_name
                            FROM accidents
                            GROUP BY month, LSOA_name""")
    df = pd.DataFrame(per_month, columns=['count', 'month', 'LSOA_name'])
    df = df.set_index('LSOA_name')
    df = df[df['month'] == target_month]
    df = df[df['count'] >= 2]
    return df.index
    # print(df.nlargest(15,'count'))


# make_db()
# load_data('E:\\data\\data')
# clean_data()
#predict_burglary()

def vis_results(output: dict):
    # load Barnet deprivation data
    df_depr = pd.read_excel('ID 2019 for London.xlsx ', sheet_name='IMD 2019')
    df_depr_barn = df_depr[df_depr['Local Authority District name (2019)'] == 'Barnet']

    # load London LSOA geometry data
    ldn_df = gpd.read_file('LSOA_2011_London_gen_MHW.shp')
    ldn_df.rename(columns={'LSOA11CD': 'LSOA code (2011)'}, inplace=True)

    # load ward geometry data
    wards_gdf = gpd.read_file('Wards_December_2022_Boundaries_UK_BGC_Barnet.geojson')
    wards_gdf = wards_gdf[wards_gdf['LAD22NM'] == 'Barnet']

    # load major road geometry data
    #roads_df = gpd.read_file('Major_Road_Network_2018_Open_Roads.shp')

    # join deprivation data and lsoa boundaries
    df = pd.merge(df_depr_barn, ldn_df, on='LSOA code (2011)')
    gdf = gpd.GeoDataFrame(df)
    gdf.rename(columns={'Index of Multiple Deprivation (IMD) Score': 'MultipleDeprivation'}, inplace=True)

    # Create Visualisation of Barnet LSOAs and Roads
    minx, miny, maxx, maxy = gdf.total_bounds
    fig, ax = plt.subplots(1, figsize=(15, 15))
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    #roads_df.plot(ax=ax, alpha=1, column='roadClassi', edgecolor="blue")
    gdf['geometry'].plot(ax=ax, alpha=1, color='w', edgecolor="black")
    wards_gdf['geometry'].geometry.boundary.plot(ax=ax, alpha=1, edgecolor="black")
    ax.axis('off')
    ax.set_title('Scores in March 2023 (mode is seasonal)',
                 fontdict={'fontsize': '15', 'fontweight': '3'})
    # merge model output with geometric data
    output_df = pd.DataFrame()
    output_df['LSOA name (2011)'] = pd.Series(output.keys())
    output_df['output_values'] = pd.Series(output.values())
    geo_output = pd.merge(gdf[['geometry', 'LSOA name (2011)']], output_df, on='LSOA name (2011)')
    geo_output = gpd.GeoDataFrame(geo_output)
    # plot output data
    geo_output.plot(ax=ax, alpha=1, column='output_values', cmap='YlOrRd')
    sm = plt.cm.ScalarMappable(cmap='YlOrRd')#, norm=plt.Normalize(vmin=geo_output.output_values.min(),
                                                                 #vmax=geo_output.output_values.max()))
    cbar = fig.colorbar(sm, shrink=0.5)

    return plt.show()


vis_results(predict_burglary())

conn.commit()
conn.close()
