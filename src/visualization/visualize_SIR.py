

import pandas as pd
import numpy as np

import dash
dash.__version__
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

import plotly.graph_objects as go

import os
print(os.getcwd())
df_input_large=pd.read_csv('data/processed/COVID_final_set.csv',sep=';')
df_input_SIR=pd.read_csv('data/processed/COVID_SIR_model.csv',sep=';')


fig = go.Figure()

app = dash.Dash()

colors = {
    'background': '#111111',
    'text': '#7FDBFF' }

app.layout = html.Div([html.H1(children='Applied Data Science on COVID-20 data', style={'color':'red'}),

    dcc.Markdown('''
    The goal of the project is to track Coronavirus spread across countries as the general information available on the internet is not so relevant and informative and to have a deep dive into local development of the spread and predict the future spread.
    This project has been tackled using CRISP-DM approach and major emphasis has been laid on automating the data gathering process, filtered and transformed the gathered data, using machine learning for calculating the doubling rate, developing a SIR Model for forecasting the future spread and finally deploying on a responsive dashboard

    '''),

    html.Div([dcc.Markdown('''
    ## Select Multiple Country for visualization
    ''', style={'color':'green'}),


    dcc.Dropdown(
        id='country_drop_down',
        options=[ {'label': each,'value':each} for each in df_input_large['country'].unique()],
        value=['US', 'Germany','Italy'], # which are pre-selected
        multi=True
    )], style={'width': '30%', 'display': 'inline-block','border':'2px black solid', 'borderRadius':5}),

    html.Div([dcc.Markdown('''
        ## Select Timeline of confirmed COVID-20 cases or the approximated doubling time
        ''', style={'color':'green'}),


    dcc.RadioItems(
    id='doubling_time',
    options=[
        {'label': 'Timeline Confirmed ', 'value': 'confirmed'},
        {'label': 'Timeline Confirmed Filtered', 'value': 'confirmed_filtered'},
        {'label': 'Timeline Doubling Rate', 'value': 'confirmed_DR'},
        {'label': 'Timeline Doubling Rate Filtered', 'value': 'confirmed_filtered_DR'},
    ],
    value='confirmed',

    labelStyle={'display': 'inline-block'}
    )],style={'width': '68%', 'float': 'right', 'display': 'inline-block','border':'2px black solid', 'borderRadius':5}),

    dcc.Graph(figure=fig, id='main_window_slope'),


    html.Div([html.H1(
        children='SIR Simulation Curve',
        style={
            'textAlign': 'center',
            'color': colors['#ffa37f']
        }
    )]),

    html.Div([dcc.Markdown('''
    ## Select Multiple Country for SIR modeling curve
    ''', style={'color':'green'}),

    dcc.Dropdown(
        id='country_drop_SIR_down',
        options=[ {'label': each,'value':each} for each in df_input_SIR.columns[1:101]],
        value=['US', 'Germany','India'], # which are pre-selected
        multi=True
    )], style={'display': 'inline-block','border':'2px black solid', 'borderRadius':5}),


    dcc.Graph(figure=fig, id='main_SIR_slope'),


     ], style={'padding':10})





@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('country_drop_down', 'value'),
    Input('doubling_time', 'value')])
def update_figure(country_list,show_doubling):


    if 'doubling_rate' in show_doubling:
        my_yaxis={'type':"log",
               'title':'Approximated doubling rate over 3 days (larger numbers are better #stayathome)'
              }
    else:
        my_yaxis={'type':"log",
                  'title':'Confirmed infected people (source johns hopkins csse, log-scale)'
              }


    traces = []
    for each in country_list:

        df_plot=df_input_large[df_input_large['country']==each]

        if show_doubling=='doubling_rate_filtered':
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.mean).reset_index()
        else:
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.sum).reset_index()
       #print(show_doubling)


        traces.append(dict(x=df_plot.date,
                                y=df_plot[show_doubling],
                                mode='markers+lines',
                                marker={'size': 3, 'opacity': 0.5},
                                line= {'width':2, 'opacity' :0.9,},
                                name=each
                        )
                )

    return {
            'data': traces,
            'layout': dict (
                width=1280,
                height=720,

                xaxis={'title':'Timeline',
                        'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=14,color="#7f7f7f"),
                      },
                 hovermode='closest',

                yaxis=my_yaxis,
                plot_bgcolor=colors['background'],
                paper_bgcolor= colors['background'],
        )
    }

@app.callback(
    Output('main_SIR_slope', 'figure'),
    [Input('country_drop_SIR_down', 'value')])

def update_figure(country_list):

    traces = []

    for each in country_list:



        traces.append(dict(x=df_input_SIR.Date,
                                y=df_input_SIR[each],
                                mode='markers+lines',
                                marker={'size': 3, 'opacity': 0.5},
                                line= {'width':2, 'opacity' :0.9,},
                                name=each
                        )
                )
        traces.append(dict(x=df_input_SIR.Date,
                                y=df_input_SIR[each+'_SIR'],
                                mode='markers+lines',
                                marker={'size': 3, 'opacity': 0.5},
                                line= {'width':2, 'opacity' :0.9,},
                                name=each+'_SIR'
                        )
                )

    return {
            'data': traces,
            'layout': dict (
                width=1280,
                height=720,

                xaxis={'title':'Timeline',
                        'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=14,color="#7f7f7f"),
                      },
                 hovermode='closest',

                yaxis={'type':"log",
               'title':'SIR prediction'
              },plot_bgcolor=colors['background'],
                paper_bgcolor= colors['background'],
        )
    }


if __name__ == '__main__':

    app.run_server(debug=True, use_reloader=False)
