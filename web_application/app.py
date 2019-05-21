
# coding: utf-8

# In[5]:


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import pandas as pd

app = dash.Dash()

df = pd.read_csv('./dummy.csv')

org = 42662873

def new_data(org):
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
        df_new = df_new[['EIN', 'fin_labels', 'text_labels', 'geo_labels', 'fin_dist_'+str(fin), 'text_dist_'+str(text), 'geo_dist_'+str(geo)]]

        x = df_new['fin_dist_'+str(fin)].values
        y = df_new['text_dist_'+str(text)].values
        z = df_new['geo_dist_'+str(geo)].values
        
        return x, y, z
    
    else:

        return None

## need to pick top x "closest" orgs for each cluster type instead of pulling in entire cluster for each

x, y, z = new_data(org)

# image_filename = '/Users/erinhansen/Downloads/image1.png' # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

#     html.Div(
#         html.Img(src='data:image/png;base64,{}'.format(encoded_image))
#     ),
    
    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    
    html.Div([
        dcc.Input(id='input-1-keypress', type='text', value='TEST'),
        html.Div(id='output-keypress')
    ]),
    
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {
                    'x': x, 
                    'y': y, 
                    'z': z, 
                    'type': 'scatter3d', 
                    'name': 'cluster 1',
                    'mode': 'markers'
                },
            ],
            'layout': {
                'title': 'Visualizing Org: ' + str(org),
                'height': 900, 
            }
        }
    )
])

@app.callback(Output('output-keypress', 'children'),
              [Input('input-1-keypress', 'value')])
def update_output(input1):
    return u'Input 1 is "{}"'.format(input1)

if __name__ == '__main__':
    app.run_server(debug=False)