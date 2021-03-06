import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import base64
import pandas as pd
import math
from nltk.stem import WordNetLemmatizer
import re
import math
# from sklearn import preprocessing

# scaler = preprocessing.MinMaxScaler()
LEMMA = WordNetLemmatizer()

app = dash.Dash()

df = pd.read_csv('./data/data_for_viz.csv', dtype= {'EIN':'object'})
df = df.fillna(0)

def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


# def scaleColumns(df, cols_to_scale, scaler):
#     for col in cols_to_scale:
#         df[col] = pd.DataFrame(scaler.fit_transform(pd.DataFrame(df[col])),columns=[col])
#     return df


def new_data(org, limit, plot):
    if len(df[df['EIN']==org]) > 0:
        col = 'EIN'
    elif len(df[df['name']==org]) > 0:
        col = 'name'
    else:
        col = None
        
    if col:
        fin = int(df[df[col]==org]['fin_labels'].values)
        text = int(df[df[col]==org]['text_labels'].values)
#         geo = int(df[df[col]==org]['geo_labels'].values)

        df_new = df[df['fin_labels'] == fin].append(df[df['text_labels'] == text])#.append(df[df['geo_labels'] == geo])
        df_new = df_new[['EIN', 'name', 'fin_labels', 'text_labels', 'latitude', 'longitude', 
                         'fin_dist_'+str(fin), 'text_dist_'+str(text)]]
        df_new['color'] = [1 if c == org else 0 for c in df_new[col]]
        
        df_new['geo_dist'] = df_new.apply(lambda x: distance(df_new.loc[df_new[col] == org][['latitude','longitude']].values[0].tolist(),[x['latitude'],x['longitude']]), axis=1)
#         df_new = scaleColumns(df_new, list(['geo_dist']), scaler)
        
        color = df_new['color'].values
        if len(color) > limit:
            color = color[:limit]
            
        name = df_new['name'].values
        if len(name) > limit:
            name = name[:limit]
        
        if plot == 'scatter':
            x = df_new['fin_dist_'+str(fin)].values
            y = df_new['text_dist_'+str(text)].values
            z = df_new['geo_dist'].values
            
            if len(x) > limit:
                x = x[:limit]
            if len(y) > limit:
                y = y[:limit]
            if len(z) > limit:
                z = z[:limit]
            return x, y, z, name, color
        
        elif plot == 'map':
            lat = df_new['latitude'].values
            lon = df_new['longitude'].values
            
            if len(lat) > limit:
                lat = lat[:limit]
            if len(lon) > limit:
                lon = lon[:limit]
            return lat, lon, name, color
        else:
            return None
        
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

def highlighter(mission, topic):
    highlighted_mission = [html.Span(word, style={'backgroundColor': 'rgb(244,208,63)'}) 
                               if re.sub('[^a-zA-Z ]', '', LEMMA.lemmatize(word)).lower() in topic 
                               else " "+str(word)+" " for word in mission.split(" ")]
    return highlighted_mission


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
              dcc.Input(id='input-1-keypress', type='text', value='952266749'),
              html.Div(id='output-keypress')
             ], style={'textAlign': "left", "padding-left": "30px", "padding-top": "100px", "font-family": "Verdana, sans-serif"}),
    
    ### RADIO ###
    html.Div([dcc.RadioItems(
                id='radio',
                options=[
                    {'label': ' Financial ', 'value': 'F'},
                    {'label': ' Text', 'value': 'T'},
                    {'label': ' Geographic ', 'value': 'G'}
                ],
                value='F',
                labelStyle={'display': 'inline-block', "padding-top": "30px", "padding-left": "15px",
                            "font-family": "Verdana, sans-serif"})
    ]),
    
    ### METRICS SIDEBAR ###
    html.Div([html.Div([html.Div(id='metrics-title')]),
              html.Div([html.Div(id='metrics-content')]),
              html.Div([dcc.Graph(id = 'metrics-plot')], style ={"width": "450px"}),
             ], style={"float": "left", "width": "500px", "padding-left": "30px", "padding-top": "30px", 
                       "font-family": "Verdana, sans-serif", "font-weight": "normal"}),    
    
    ### SCATTER PLOT ###
    html.Div([dcc.Graph(id="scatter-plot")
             ], style={"position": "absolute", "right": "10px", "bottom": "10px", "width": "1000px"})

    

])



### METRICS TITLE ###
@app.callback(Output("metrics-title", 'children'),
              [Input('input-1-keypress', 'value'),
               Input('radio', 'value')]
             )
def update_metrics_title(org, radio):
    name = get_org_metric(org, 'name')
    
    if radio == 'F':
        return [html.P("Financial Metrics for " + str(name), style={'fontSize': 24})]
    elif radio == 'T':
        return [html.P("Description of Text Data for " + str(name), style={'fontSize': 24})]
    elif radio == 'G':
        return [html.P("Geographic Location of " + str(name), style={'fontSize': 24})]
    else:
        return None
    
    
    
### METRICS CONTENT ###
@app.callback(Output("metrics-content", 'children'),
              [Input('input-1-keypress', 'value'),
               Input('radio', 'value')]
             )
def update_metrics_content(org, radio):
    name = get_org_metric(org, 'name')
    if radio == 'F':
        gr1 = get_org_metric(org, 'gross_receipts')
        r1 = get_org_metric(org, 'revenue')
        fb1 = get_org_metric(org, 'fund_balance')
        l1 = get_org_metric(org, 'liabilities')
        return [html.P("Org Financials Against Peer Group"),
                html.Div([html.H5("Gross Receipts: "+'${:,.0f}'.format(gr1))], style={'padding-left':'30'}),
                html.Div([html.H5("Revenue: "+'${:,.0f}'.format(r1))], style={'padding-left':'30'}),
                html.Div([html.H5("Fund Balance: "+'${:,.0f}'.format(fb1))], style={'padding-left':'30'}),
                html.Div([html.H5("Liabilities: "+'${:,.0f}'.format(l1))], style={'padding-left':'30'})
               ]
    elif radio == 'T':
        mission = get_org_metric(org, 'mission')
        topic = get_org_metric(org, 'topic')
        return [html.P("Org Mission Statement"),
                html.Div([html.H5(highlighter(mission, topic))], style={'padding-left':'30'}),
                html.P("Common Keywords for Peer Group"),
                html.Div([html.H5(str(topic))], style={'padding-left':'30'})]
    elif radio == 'G':
        county = get_org_metric(org, 'county')
        return [html.P("Org County"),
                html.Div([html.H5(str(county))], style={'padding-left':'30'})]
    else:
        return None

    
### REMOVE GRAPH FOR TEXT ### 
@app.callback(Output("metrics-plot", 'style'),
               [Input('radio', 'value')]
             )

def update_style(radio):
    if radio == 'T':
        style = {'display':'none'}
    else:
        return None
    return style    
    
### METRICS PLOT ###
@app.callback(Output("metrics-plot", 'figure'),
              [Input('input-1-keypress', 'value'),
               Input('radio', 'value')]
             )

def update_metrics_plot(org, radio):
    if radio == 'F':
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
                          opacity = 0.6,
                          name = 'Peer Group',
                          hoverinfo='name'
                        ),
                        go.Scatterpolar(
                          r = [gr1, r1, fb1, l1, gr1],
                          theta = ['Gross Receipts','Revenue','Fund Balance', 'Liabilities', 'Gross Receipts'],
                          fill = 'toself',
                          fillcolor = 'rgb(244,208,63)',
                          line =  dict(
                                color = 'rgb(244,208,63)'
                            ),
                          opacity = 0.6,
                          name = 'Org',
                          hoverinfo='name'
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
    elif radio == 'G':
        lat, lon, name, color = new_data(org, 100000, 'map')
#         name = get_org_metric(org, 'name')
        trace = [go.Scattergeo(locationmode='USA-states', lon=lon, lat=lat,
                           text=name, hoverinfo='text', showlegend=False, mode='markers',
                           marker={'size': 8, 'opacity': 0.8, 'symbol': "diamond", "color": color, 
                                   'colorscale': [[0, 'rgb(26, 82, 118)'],[1, 'rgb(244,208,63)']],
                                   'line': {'width': 0.1, 'color': 'rgba(102, 102, 102)'}})]
        layout = go.Layout(geo={'scope': 'usa', 'projection': {'type': 'albers usa'}, 'showland': True,
                   'landcolor': "#c7c7c7", 'subunitcolor': "black",
                   'countrycolor': "black", 'countrywidth': 0.5, 'subunitwidth': 0.5},
                    autosize=False,
                    width=500,
                    height=500,
                    margin=go.layout.Margin(
                        l=0,
                        r=0,
                        b=0,
                        t=0,
                        pad=0
                    )
                   )
        return {"data": trace, "layout": layout}
    else:
        []
    
    

### SCATTERPLOT ###
@app.callback(Output("scatter-plot", "figure"),
              [Input('input-1-keypress', 'value')])

def update_scatter(org):
    x, y, z, name, color = new_data(org, 100000, 'scatter')
    
    trace = [go.Scatter3d(
        x=x, y=y, z=z, text=name, hoverinfo='text',
        mode='markers', marker={'size': 8, 'color': color, 
                                'colorscale': [[0, 'rgb(26, 82, 118)'],[1, 'rgb(244,208,63)']]
                                , 'opacity': 0.8, 
                                "showscale": False, "colorbar": {"thickness": 15, "len": 0.5, "x": 0.8, "y": 0.6, }, })
            ]
    return {"data": trace,
            "layout": go.Layout(
                scene={"aspectmode": "cube", "xaxis": {"title": f"Financial", },
                       "yaxis": {"title": f"Text", },
                       "zaxis": {"title": f"Geographic", }},
                autosize=False,
                        width=900,
                        height=850,
                        margin=go.layout.Margin(
                            l=10,
                            r=10,
                            b=10,
                            t=10,
                            pad=10
                        ))
            }

if __name__ == '__main__':
    app.run_server(host="0.0.0.0",debug=False)