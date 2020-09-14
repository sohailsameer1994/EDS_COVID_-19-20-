import pandas as pd
import numpy as np

from datetime import datetime

def store_flat_data():
    data_path='data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    DF_raw=pd.read_csv(data_path)
    EDA_Full_data=pd.DataFrame(np.array(DF_raw.columns[4:]), columns=['Date']) # converting the present dataframe into more readable and easily plotable dataframe
    allcountries= list (DF_raw['Country/Region'].unique())

    for each in allcountries:
        EDA_Full_data[each]= np.array(DF_raw[DF_raw['Country/Region']== each].iloc[:,4::].sum())


    time_idx=[datetime.strptime( each,"%m/%d/%y") for each in EDA_Full_data.Date] # convert to datetime
    time_str=[each.strftime('%Y-%m-%d') for each in time_idx] # convert back to date ISO norm (str)
    EDA_Full_data['Date']= time_idx
    EDA_Full_data.to_csv('data/processed/COVID_full_flat_table.csv',sep=';',index=False)
    print(' Number of rows stored: '+str(EDA_Full_data.shape[0]))




def store_relational_JH_data():

    ''' Transformes the COVID data into a  relational data set which can be used for modeling

    '''

    path='data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    raw_data = pd.read_csv(path)

    base_df =raw_data.rename(columns={'Country/Region':'country',
                      'Province/State':'state'})

    base_df['state']=base_df['state'].fillna('no')

    base_df=base_df.drop(['Lat','Long'],axis=1)


    pd_relational_model=base_df.set_index(['state','country']) \
                                .T                              \
                                .stack(level=[0,1])             \
                                .reset_index()                  \
                                .rename(columns={'level_0':'date',
                                                   0:'confirmed'},
                                                  )

    pd_relational_model['date']=pd_relational_model.date.astype('datetime64[ns]')

    pd_relational_model.to_csv('data/processed/COVID_relational_confirmed.csv',sep=';',index=False)
    print(' Number of rows stored: '+str(pd_relational_model.shape[0]))
    print(' Latest date is: '+str(max(pd_relational_model.date)))

def store_population_data():
    ''' Transformes the Population data to a required form and matching data to covid data

    '''

    df_pop=pd.read_csv('data/raw/Data_Extract_From_World_Development_Indicators/Population.csv ')
    df_P= df_pop[['Country Name', '2019 [YR2019]']] #considering latest population
    df_P=df_P.rename(columns={'Country Name':'country',
                             '2019 [YR2019]':'population'})
    df_P = df_P.iloc[0:217,:] # as we hust need distinct countries
    df_P['country'] = df_P['country'].replace(['Bahamas, The', 'Brunei Darussalam', 'Myanmar','Congo, Dem. Rep.',
                                       'Congo, Rep.','Czech Republic','Egypt, Arab Rep.','Gambia, The','Iran, Islamic Rep.','Korea, Rep.',
                                      'Kyrgyz Republic','Lao PDR', 'Russian Federation','St. Kitts and Nevis','St. Lucia','St. Vincent and the Grenadines',
                                      'Slovak Republic', 'Syrian Arab Republic','United States','Venezuela, RB','Yemen, Rep.'],
                                      ['Bahamas','Brunei','Burma','Congo (Brazzaville)','Congo (Kinshasa)','Czechia','Egypt',
                                       'Gambia','Iran','Korea, South', 'Kyrgyzstan', 'Laos', 'Russia', 'Saint Kitts and Nevis',
                                        'Saint Lucia', 'Saint Vincent and the Grenadines', 'Slovakia', 'Syria', 'US',
                                       'Venezuela', 'Yemen'])
    df_P['population'] = df_P['population'].replace('..',3214000)
    df_P2 = pd.DataFrame([['Diamond Princess', 2670], ['Holy See', 825],['MS Zaandam', 1432],['Taiwan', 23780000],['Western Sahara',652271]], columns=['country', 'population'])
    df_P=df_P.append(df_P2, ignore_index=True) # Adding additional countries
    df_P['population']=df_P.population.astype(int)
    df_P.to_csv('data/processed/world_population.csv',sep=';',index=False)
    print(str(df_P.shape[0])+ ' countries population information stored: ')



if __name__ == '__main__':

    store_flat_data()
    store_relational_JH_data()
