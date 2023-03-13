from dash import Dash, dcc, html, Input, Output,State,ctx, dash_table
import os
import pandas as pd
from kmodes.kmodes import KModes
import plotly.graph_objects as go
import plotly.express as  px

import numpy as np
import math
from utils_y import yelp_scrapper





external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

scrapper=yelp_scrapper()

# app layout
app.layout=html.Div([
    html.Div([
        html.Div(id='url-div',children=[dcc.Input(id='yelp-url'
            ,placeholder='eg: https://www.yelp.com/biz/applebees-grill-bar-san-francisco'
            ,style={'width':'100%'})],style={'width':'40%','display':'inline-block'}),
        html.Div([dcc.Dropdown(id='n-pages',options=[{'label':str(i)+' pages','value':i} for i in range(1,11)],value=10)]
            ,style={'width':'10%','display':'inline-block','position':'absolute','margin-left':'1%'}),
         html.Div([html.Button('Scrap!',id='scrp-btn',n_clicks=0)],style={'display':'inline-block','margin-left':'12%'}),
        html.Div(id='scrapper-results')

    ])
])

@app.callback(Output('scrapper-results','children'),
                    [Input('scrp-btn','n_clicks'),
                    State('yelp-url','value'),
                    State('n-pages','value')])
def get_results(n_clicks,url,n_pages):


     if 'scrp-btn'==ctx.triggered_id:
        #print(url,n_pages)
        n_pages=int(n_pages)

        if n_pages==1:
            res=scrapper.multi_pages(url,n_pages)
        else:
            
            res=scrapper.multi_pages(url,n_pages)
        
        reviews=scrapper.create_yelp_df(res)

        reviews_data_table=dash_table.DataTable(
                                id='reviews-table',
                                style_table={'height':'500px','overflowY':'auto','overflowX':'auto','width':'auto'},
                                style_header={'backgroundColor': '#393F56','fontWeight': 'bold','color':'white'},
                                style_cell={'textAlign':'left','textOverflow': 'ellipsis','overflow': 'hidden','maxWidth': 0},
                                export_format='csv',
                                page_size=10,
                                columns=[{'name':i,'id':i} for i in reviews.columns],
                                data=reviews.to_dict('records')
            )


        return reviews_data_table
    
    




# this callback triggers kmodes algorithm



if __name__=='__main__':
    app.run_server(debug=True)
