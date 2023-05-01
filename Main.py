import os
import sqlite3
import pandas as pd

conn = sqlite3.connect('database.db')
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
    deletec_value = []
    for folder in os.listdir(directory):
        for file in os.listdir('E:\\data\\data\\'+folder):
            print(file)
            if 'city-of-london' in file:
                data = pd.read_csv('E:\\data\\data\\'+folder+'\\'+file)
                for line in data.iterrows():
                    values = ', '.join("'" + str(x) + "'" for x in line[1])
                    data_line = values.split(',')
                    if len(data_line) == 10:
                        data_line.append(data_line[9])
                        data_line[9] = ' NaN'
                        data_line.append(' NaN')
                        values = ', '.join("'" + str(x) + "'" for x in data_line)
                    try:
                        c.execute('INSERT INTO accidents (Crime_ID, Month, Reported_by, Falls_within, Longitude, Latitude, Location, LSOA_code, LSOA_name, Crime_type, Last_outcome_category, Context) VALUES ('+values+ ')')
                    except:
                        deletec_value.append(values)
    print(deletec_value)

def clean_data():
    c.execute("""DELETE FROM accidents
                WHERE Crime_type IS NOT 'burglary'
                """)

#make_db()
#load_data('E:\\data\\data')
clean_data()




conn.commit()
conn.close()