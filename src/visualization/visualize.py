import dash
dash.__version__
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

import plotly.graph_objects as go
df_input_large=pd.read_csv('/data/processed/COVID_final_set.csv',sep=';')

fig = go.Figure()
app = dash.Dash()

app.layout = html.Div([html.H1(children='Applied Data Science on COVID-19 data', style={'color':'blue'}),

    dcc.Markdown('''
    The goal of the project is to track Coronavirus spread across countries as the general information available on the internet is not so relevant and informative and to have a deep dive into local development of the spread and predict the future spread.
    This project has been tackled using CRISP-DM approach and major emphasis has been laid on automating the data gathering process, filtered and transformed the gathered data, using machine learning for calculating the doubling rate, developing a SIR Model for forecasting the future spread and finally deploying on a responsive dashboard'''),

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
        ## Select Timeline of confirmed COVID-19 cases or the approximated doubling time
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

    dcc.Graph(figure=fig, id='main_window_slope')
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
                                line= {'width':1, 'opacity' :0.9,},
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

                yaxis=my_yaxis
        )
    }

if __name__ == '__main__':

    app.run_server(debug=True, use_reloader=False)
