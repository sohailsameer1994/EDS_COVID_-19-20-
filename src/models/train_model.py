import pandas as pd
import numpy as np

from datetime import datetime
import pandas as pd

from scipy import optimize
from scipy import integrate

%matplotlib inline
import matplotlib as mpl
import matplotlib.pyplot as plt

import seaborn as sns


sns.set(style="darkgrid")

mpl.rcParams['figure.figsize'] = (16, 9)
pd.set_option('display.max_rows', 500)

from PIL import Image


def model_sir():
    df_pop=pd.read_csv('data/processed/world_population.csv',sep=";")

    df_data=pd.read_csv('data/processed/COVID_full_flat_table.csv',sep=';')
    df_data=df_data.iloc[60:,:] #removing first 50 days of covid spread as the data is inconsistent
    df_data=df_data.drop(['Taiwan*'], axis= 1) # dropping taiwan as the data is inconsistent


    df_data=df_data.reset_index()
    df_data=df_data.drop(['index'], axis=1)
    df_data=df_data.rename(columns={'level_0':'index'})


    df= pd.DataFrame(df_data.loc[0])
    df=df.reset_index()
    df = df.iloc[1:]
    country_list= list(df[df[0]>38]['index']) #finding countries with significant number of covid cases i.e,>38
    country_list.insert(0, 'Date')

    df_data=df_data[country_list] # confining data frame to that perticular countries



    for each in country_list[1:]:
        ydata = np.array(df_data[each])
        t=np.arange(len(ydata))
        N0= df_pop[df_pop['country']== each]['population']
        I0=ydata[0]
        S0 = N0-I0
        R0=0
        def SIR_model_t(SIR,t,beta,gamma):


            ''' Simple SIR model
        S: susceptible population (populatin that can be effected)
        I: infected people (population already infected)
        R: recovered people (population recovered from COVID)
        beta:

        overall condition is that the sum of changes (differnces) sum up to 0
        dS+dI+dR=0
        S+I+R= N (constant size of population)

    '''
            S,I,R=SIR
            dS_dt=-beta*S*I/N0          #S*I is the
            dI_dt=beta*S*I/N0-gamma*I
            dR_dt=gamma*I
            return dS_dt,dI_dt,dR_dt

        def fit_odeint(t, beta, gamma):
            '''
    helper function for the integration
    '''
            return integrate.odeint(SIR_model_t, (S0, I0, R0), t, args=(beta, gamma))[:,1] # we only would like to get dI

        popt, pcov = optimize.curve_fit(fit_odeint, t, ydata,maxfev=50000)
        perr = np.sqrt(np.diag(pcov))
        fitted = fit_odeint(t, *popt).reshape((-1,1))
        df_data[each+'_SIR']= fitted
    df_data.to_csv('data/processed/COVID_SIR_model.csv',sep=';',index=False)
    print(' Number of rows stored: '+str(df_data.shape[0]))


    return df_data

if __name__ == '__main__':

    model_sir()
