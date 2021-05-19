# Import Pandas
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import accumulate
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output


app = dash.Dash(__name__)

##http://127.0.0.1:8050/
## LOAD DATASÆT
datasaet = pd.read_csv('cr286_balancingfr5s.csv', usecols=[5,6,7], index_col=2, parse_dates=True,header=0,
names=['up_imb_price','down_imb_price','Start_date'])

## INDEX DATA TIL DATE-FORMAT
#datasaet[0] = pd.to_datetime(datasaet[0])
#datasaet[3] = pd.to_datetime(datasaet[3])

## Cast datatype til float
datasaet.astype(float, errors='ignore')


## ret datafejl 
datasaet.iloc[:,0] = datasaet.iloc[:,0].div(100)
datasaet.iloc[:,1] = datasaet.iloc[:,1].div(100)

## Lav Spot_imb kolonne
datasaet['spot_imb'] = datasaet.iloc[:,0] - datasaet.iloc[:,1] 


                                ######DASH INPUT#########
app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('GPT Analyse Modul'),
                                 html.P('Visualising time series with Plotly - Slucifer'),
                                 html.P('Change values to optimize output.'),
                                html.Br(),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[html.Div(["#dages-gennemsnit: ",
                                       dcc.Input(
                                      id='num-multi',
                                         type='number',
                                           value=4)], style={'textAlign':'Right','color': 'white'}),
                                    html.Div(["#Scale: ",
                                        dcc.Input(
                                        id='num-multi1',
                                           type='number',
                                       value=1)], style={'textAlign':'Right','color': 'white'}),
                                    html.Div(["#Hurdle-rate: ",
                                          dcc.Input(
                                      id='num-multi2',
                                        type='number',
                                          value=10)], style={'textAlign':'Right','color': 'white'}),
                                    html.Div(["#obs_pr_dag: ",
                                          dcc.Input(
                                         id='num-multi3',
                                         type='number',
                                         value=48)], style={'textAlign':'Right', 'color': 'white'})
                                                ],
                                    style={'color': '#1E1E1E'} 
                                )]
                             ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(id='example-graph'),
                                html.Div(id='result', style={'color': 'white'}),
                                html.Div(id='result1', style={'color': 'white'}),
                                html.Div(id='result2', style={'color': 'white'}),
                                html.Div(id='result3', style={'color': 'white'}),
                                html.Div(id='result4', style={'color': 'white'}),
                                html.Div(id='result5', style={'color': 'white'}),
                             ])
                              ])
        ]

)

@app.callback(
    Output('example-graph', 'figure'),
    Output('result', 'children'),
    Output('result1', 'children'),
    Output('result2', 'children'),
    Output('result3', 'children'),
    Output('result4', 'children'),
    Output('result5', 'children'),
    Input('num-multi', 'value'),
    Input('num-multi1', 'value'),
    Input('num-multi2', 'value'),
    Input('num-multi3', 'value'))
                    

                            ## SLUCIFER FUNKTION TEST

def slucifer(dage=4, scale=1, hurdle=10,obs_pr_dag=48):
    count = obs_pr_dag*(dage) ##variable til at stoppe loop. Count stiger indtil antal rækker i fil -48*dage er opnået
    dage_sum = [] ##liste til at lave .mean() af antal dage i funktion
    sum = 0
    plotsum = [] ##  liste til at summere hele tidsseries profit pr. dag
    loss_days = []
 ## til at stoppe loop
    for index, value in enumerate(datasaet.spot_imb):

                if count >= len(datasaet.spot_imb):    #Stop loop before EOF
                        # Data for plotting

                        ax = px.line(datasaet, datasaet.index.values[0:len(plotsum)], list(accumulate(plotsum)),
                            labels={"x":'Periode', "y":'Profit'}, title='Slucifer spiser energimarkedet!!', template='plotly_dark').update_layout(
                                   {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
                                    

                        result = "Slucifer profit periode: {}".format(round(sum,2)) + "€ ved {}".format(int(dage)) + " dages-gennemsnit, {}".format(int(scale)) + "x positions-størrelse og større/mindre end {}".format(int(hurdle)) + "€/mwh hurdle-rate."
                        result1 = "Number of observations less lag-element: {}".format(len(plotsum)) +" half-hours"
                        result2 = "Number of observations in dataset: {}".format(int(count)) + " half-hours"
                        result3 = "Number of loss-days: {}".format(len(loss_days)) + " half-hours"
                        result4 = "Biggest loss in period: {}".format(round(min(loss_days),2)) + "$"
                        result5 = "Biggest profit in period: {}".format(round(max(plotsum),2)) + "$"
                        

                        return ax, result, result1, result2, result3, result4, result5

                #break
                
                for x in range(dage):  ##For hver dags lag gemmes spot_premium i liste dage_sum 
                        dage_sum.append(datasaet.spot_imb[index+((x+1)*obs_pr_dag)])
                        #print(dage_sum)

                if np.mean(dage_sum) > hurdle:  ## mean af #antal-dage-lag, rolling hver dag.
                    sum += datasaet.spot_imb[index] * 1 * scale ##større position ved mean>10eu/mwh
                    plotsum.append(datasaet.spot_imb[index] * scale) ##tilføj rolling dags profit til liste
                    count += 1 ##counter til at stoppe ved EOF
                    dage_sum = [] ##reset liste til at lave mean for hver dag.
                    if datasaet.spot_imb[index] * 1 <0:  ##hvis rolling-dag er tab, tilføj til loss_days liste.
                        loss_days.append(datasaet.spot_imb[index] * 1)

                elif np.mean(dage_sum) > 0 and np.mean(dage_sum) <= hurdle:  ## mean af #antal-dage-lag, rolling hver dag.
                    sum += datasaet.spot_imb[index] * 1
                    plotsum.append(datasaet.spot_imb[index])
                    count += 1
                    dage_sum = []
                    if datasaet.spot_imb[index] * 1 <0:
                        loss_days.append(datasaet.spot_imb[index] * 1)  

                elif np.mean(dage_sum) < 0 and np.mean(dage_sum) >= -hurdle:  
                    sum += datasaet.spot_imb[index] * -1
                    plotsum.append(datasaet.spot_imb[index]*-1)
                    count += 1
                    dage_sum = []
                    if datasaet.spot_imb[index] * -1 <0:
                        loss_days.append(datasaet.spot_imb[index] * -1) 
                else:
                    sum += datasaet.spot_imb[index] * -1 * scale
                    plotsum.append(datasaet.spot_imb[index]*-scale)
                    count += 1
                    dage_sum = []
                    if datasaet.spot_imb[index] * -1 <0:
                        loss_days.append(datasaet.spot_imb[index] * -1)


if __name__ == '__main__': 
    app.run_server(debug=True)
#print(datasaet.columns)
#datasaet.info()
#print(datasaet.head())
