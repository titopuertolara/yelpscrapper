from dash import Dash, dcc, html, Input, Output,State,ctx, dash_table,ALL
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
        html.Div([dcc.Dropdown(id='n-pages',options=[{'label':str(i)+' pages','value':i} for i in range(1,11)],value=1)]
            ,style={'width':'10%','display':'inline-block','position':'absolute','margin-left':'1%'}),
         html.Div([html.Button('Scrap!',id='scrp-btn',n_clicks=0)],style={'display':'inline-block','margin-left':'12%'}),
        dcc.Loading(id='table-loading',children=[html.Div(id='scrapper-results')],type='circle',style={'margin-top':'20%'}),
        html.Div(id='dummy-div'),
        dcc.Store(id='reviews-store')

    ])
])

@app.callback(Output('scrapper-results','children'),
              Output('reviews-store','data'),
                [Input('scrp-btn','n_clicks'),
                State('yelp-url','value'),
                State('n-pages','value')])
def get_results(n_clicks,url,n_pages):

     reviews_data_table=""
     reviews=pd.DataFrame()
     if 'scrp-btn'==ctx.triggered_id:
        #print(url,n_pages)
        n_pages=int(n_pages)
        

        try:

            if n_pages==1:
                res=scrapper.multi_pages(url,n_pages)
            else:
                
                res=scrapper.multi_pages(url,n_pages)
            
            reviews=scrapper.create_yelp_df(res)

            reviews_data_table=dash_table.DataTable(
                                    id={'type':'datatable','index':'reviews-table'},
                                    style_table={'height':'500px','overflowY':'auto','overflowX':'auto','width':'auto'},
                                    style_header={'backgroundColor': '#393F56','fontWeight': 'bold','color':'white'},
                                    style_cell={'textAlign':'left','textOverflow': 'ellipsis','overflow': 'hidden','maxWidth': 0},
                                    export_format='csv',
                                    page_size=20,
                                    columns=[{'name':i,'id':i} for i in reviews.columns],
                                    data=reviews.to_dict('records'),
                                    tooltip_data=[{column: 
                                        {
                                            'value': str(value), 'type': 'markdown'} for column, value in row.items()
                                        } for row in reviews.to_dict('records')
                                    ],
                                    row_selectable="single"

                )
        except:
            reviews_data_table="something's wrong, make sure this is a yelp link"



     return reviews_data_table,reviews.to_json()
    
@app.callback(Output('dummy-div','children'),
              [Input({'type':'datatable','index':ALL},'derived_virtual_selected_rows'),
              Input('reviews-store','data')])  
def show_insights(table_index,stored_reviews):
    reviews_df=pd.read_json(stored_reviews)
    print(reviews_df)
    return ''




# this callback triggers kmodes algorithm



if __name__=='__main__':
    app.run_server(debug=True)
