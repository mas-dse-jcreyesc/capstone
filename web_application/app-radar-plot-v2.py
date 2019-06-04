import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import base64
import pandas as pd
import math

app = dash.Dash()

df = pd.read_csv('./data/dummy.csv', dtype= {'EIN':'object'})


def new_data(org, limit):
    if len(df[df['EIN']==org]) > 0:
        col = 'EIN'
    elif len(df[df['name']==org]) > 0:
        col = 'name'
    else:
        col = None
        
    if col:
        fin = int(df[df[col]==org]['fin_labels'].values)
        text = int(df[df[col]==org]['text_labels'].values)
        geo = int(df[df[col]==org]['geo_labels'].values)

        df_new = df[df['fin_labels'] == fin].append(df[df['text_labels'] == text]).append(df[df['geo_labels'] == geo])
        df_new = df_new[['EIN', 'name', 'fin_labels', 'text_labels', 'geo_labels', 'fin_dist_'+str(fin), 'text_dist_'+str(text), 'geo_dist_'+str(geo)]]
        df_new['color'] = [1 if c == org else 0 for c in df_new[col]] 

        x = df_new['fin_dist_'+str(fin)].values
        y = df_new['text_dist_'+str(text)].values
        z = df_new['geo_dist_'+str(geo)].values
        color = df_new['color'].values
        
        if len(x) > limit:
            x = x[:limit]
        if len(y) > limit:
            y = y[:limit]
        if len(z) > limit:
            z = z[:limit]
        if len(color) > limit:
            color = color[:limit]
        
        return x, y, z, color
    
    else:

        return None

    
def get_org_metric(org, metric):
    try:
        value = df[df['EIN']==org][metric].values[0]
    except:
        value = df[df['name']==org][metric].values[0]
    return value



def get_cluster_metric(org, metric):
    try:
        label = int(df[df['EIN']==org]['fin_labels'].values)
    except:
        label = int(df[df['name']==org]['fin_labels'].values)

    value = df[df['fin_labels'] == label][metric].mean()
        
    return value

classy_img = './image/classy.png' # replace with your own image
classy_encoded = base64.b64encode(open(classy_img, 'rb').read())
ucsd_img = './image/ucsd.png' # replace with your own image
ucsd_encoded = base64.b64encode(open(ucsd_img, 'rb').read())

app.layout = html.Div(children=[
    
    ### TITLE ###
    html.Div([
        html.Div([html.P("Mapping of U.S. Non-Profit Organizations")
             ], style={"font-family": "Verdana, sans-serif", 'fontSize': 36 , 'display': 'inline-block'}),
        
        html.Img(src='data:image/png;base64,{}'.format(classy_encoded.decode())
                 , style={'height': 70, 'width': 70, "padding-left": "200px", "padding-right": "10px"}),
        html.Img(src='data:image/png;base64,{}'.format(ucsd_encoded.decode())
                 , style={'height': 60, 'width': 250, "padding-right": "10px"})
    ], style={'display': 'inline-block', 'float': 'right'}),
    
    ### USER INPUT ###
    html.Div([html.P("Org Name/EIN"),
              dcc.Input(id='input-1-keypress', type='text', value='111'),
              html.Div(id='output-keypress')
             ], style={'textAlign': "left", "padding-left": "30px", "padding-top": "100px", "font-family": "Verdana, sans-serif"}),
    
    ### METRICS SIDEBAR ###
    html.Div([html.Div([html.Div(id='metrics-title')]),
              html.P("Org Financials Against Peer Group"),
              ## placeholder for radar plot ##
              
              html.Div([
                dcc.Graph(id = 'radar-plot')
              ], style ={"width": "450px"}),
              
              ###
              html.P("Org Mission Statement"),
              html.Div([html.Div(id='mission')]),
              html.P("Common Keywords for Peer Group"),
              html.Div([html.Div(id='topic')]),
              html.P("Org County"),
              html.Div([html.Div(id='county')])
             ], style={"float": "left", "width": "500px", "padding-left": "30px", "padding-top": "30px", 
                       "font-family": "Verdana, sans-serif", "font-weight": "normal"}),
    
    
    ### SCATTER PLOT ###
    html.Div([dcc.Graph(id="scatter-plot")
             ], style={"position": "absolute", "right": "10px", "bottom": "0px", "width": "1200px"})

    

])



### METRICS TITLE ###
@app.callback(Output("metrics-title", 'children'),
              [Input('input-1-keypress', 'value')])
def update_metrics_title(org):
    name = get_org_metric(org, 'name')
    return [html.P("Metrics for " + str(name), style={'fontSize': 24})]

### MISSION STATEMENT ###
@app.callback(Output("mission", 'children'),
              [Input('input-1-keypress', 'value')])
def update_mission(org):
    mission = get_org_metric(org, 'mission')
    return [html.Div([html.H5(str(mission))], style={'padding-left':'30'})]

### TOPIC KEYWORDS ###
@app.callback(Output("topic", 'children'),
              [Input('input-1-keypress', 'value')])
def update_topic(org):
    topic = get_org_metric(org, 'topic')
    return [html.Div([html.H5(str(topic))], style={'padding-left':'30'})]

### COUNTY ###
@app.callback(Output("county", 'children'),
              [Input('input-1-keypress', 'value')])
def update_county(org):
    county = get_org_metric(org, 'county')
    return [html.Div([html.H5(str(county))], style={'padding-left':'30'})]



### RADAR PLOT ###
@app.callback(Output("radar-plot", "figure"),
              [Input('input-1-keypress', 'value')])

def update_radar(org):
    gr1 = get_org_metric(org, 'gross_receipts')
    r1 = get_org_metric(org, 'revenue')
    fb1 = get_org_metric(org, 'fund_balance')
    l1 = get_org_metric(org, 'liabilities')
    
    gr2 = get_cluster_metric(org, 'gross_receipts')
    r2 = get_cluster_metric(org, 'revenue')
    fb2 = get_cluster_metric(org, 'fund_balance')
    l2 = get_cluster_metric(org, 'liabilities')
    
    mx = max([gr1, r1, fb1, l1, gr2, r2, fb2, l2])
    mx = int(math.ceil(mx / 10**6)) * 10**6
    
    return {"data": 
                [
                  go.Scatterpolar(
                      r = [gr2, r2, fb2, l2, gr2],
                      theta = ['Gross Receipts','Revenue','Fund Balance', 'Liabilities', 'Gross Receipts'],
                      fill = 'toself',
                      fillcolor = 'rgb(26, 82, 118)',
                      line =  dict(
                            color = 'rgb(26, 82, 118)'
                        ),
                      opacity = 0.8,
                      name = 'Peer Group'
                    ),
                    go.Scatterpolar(
                      r = [gr1, r1, fb1, l1, gr1],
                      theta = ['Gross Receipts','Revenue','Fund Balance', 'Liabilities', 'Gross Receipts'],
                      fill = 'toself',
                      fillcolor = 'rgb(244,208,63)',
                      line =  dict(
                            color = 'rgb(244,208,63)'
                        ),
                      opacity = 0.8,
                      name = 'Org'
                    )
                ], 
                "layout": go.Layout(
                      polar = dict(
                        radialaxis = dict(
                          visible = True,
                          range = [0, mx]
                        )
                      ),
                      showlegend = False,
                      height = 400
                    )
                }


### SCATTERPLOT ###
@app.callback(Output("scatter-plot", "figure"),
              [Input('input-1-keypress', 'value')])

def update_scatter(org):
    x, y, z, color = new_data(org, 100)
    
    trace = [go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers', marker={'size': 8, 'color': color, 
                                'colorscale': [[0, 'rgb(26, 82, 118)'],[1, 'rgb(244,208,63)']]
                                , 'opacity': 0.8, 
                                "showscale": False, "colorbar": {"thickness": 15, "len": 0.5, "x": 0.8, "y": 0.6, }, })
            ]
    return {"data": trace,
            "layout": go.Layout(
                height=900, #title=f"Visualizing Cluster Space for<br>{org}",
                scene={"aspectmode": "cube", "xaxis": {"title": f"Financial", },
                       "yaxis": {"title": f"Text", },
                       "zaxis": {"title": f"Geographic", }})
            }

if __name__ == '__main__':
    app.run_server(debug=False)