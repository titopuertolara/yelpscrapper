from dash import Dash, dcc, html, Input, Output,State,ctx, dash_table,ALL
import os
import pandas as pd

import plotly.graph_objects as go
import plotly.express as  px

import numpy as np
import math
from utils_y import yelp_scrapper,make_graph
import random 



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)
server=app.server
scrapper=yelp_scrapper()
graphic_stars={'1':'⭐','2':'⭐⭐','3':'⭐⭐⭐','4':'⭐⭐⭐⭐','5':'⭐⭐⭐⭐⭐'}
# app layout
app.layout=html.Div([
    html.Div([
        
        html.H2('Yelp Scraper with dash'),
        html.H4('Please use it with academic purposes'),
        html.H5('Put a yelp url and you will get a table with reviews and score. Max aprox. 100 reviews per link.'),
        html.Div(id='url-div',children=[dcc.Input(id='yelp-url'
            ,placeholder='eg: https://www.yelp.com/biz/applebees-grill-bar-san-francisco'
            ,style={'width':'100%'})],style={'width':'40%','display':'inline-block'}),
        html.Div([dcc.Dropdown(id='n-pages',options=[{'label':str(i)+' pages','value':i} for i in range(1,11)],value=1)]
            ,style={'width':'10%','display':'inline-block','position':'absolute','margin-left':'1%'}),
        html.Div(dcc.Input(id='captcha',type='text'),style={'width':'10%','display':'inline-block','margin-left':'13%'}),
        html.Div([html.Button('Scrap!',id='scrp-btn',n_clicks=0)],style={'display':'inline-block','margin-left':'8%'}),
        html.Div(dcc.Loading(id='dummy-loader',children=[html.Div(id='dummy-loader-div')]),style={'display':'inline-block','margin-left':'15%'}),
        
        
        html.Div(id='sub_block_1',children=[
            dcc.Loading(id='graph-load',children=[html.Div(id='graph-div')]),
            dcc.Loading(id='wprd-load',children=[html.Div(id='wordcloud-div',style={'margin-left':'50%','margin-top':'-35%','position':'absolute'})]),
            dcc.Loading(id='text-load',children=[html.Div(id='text-review',style={'margin-left':'50%','margin-top':'-19%','position':'absolute','overflow':'scroll','height':'50%'})])
        ]),
        dcc.Loading(id='table-loading',children=[html.Div(id='scrapper-results')]
            ,type='circle'
            ,style={'margin-top':'1%'}
            ),
       
        dcc.Store(id='reviews-store'),
        dcc.Interval(id='captcha-refresh',interval=20000,n_intervals=0),
        dcc.Store(id='captcha-gen')

    ])
])

@app.callback(Output('captcha','placeholder'),
              Output('captcha-gen','data'),
              [Input('captcha-refresh','n_intervals')])
def captcha_show(n):
    n1=random.randint(0,10)
    n2=random.randint(0,10)
    out={'n1':n1,'n2':n2}
    return f'Solve {n1} + {n2}',out

@app.callback(Output('scrapper-results','children'),
              Output('reviews-store','data'),
              Output('dummy-loader-div','children'),
              Output('scrp-btn','disabled'),
                [Input('scrp-btn','n_clicks'),
                State('yelp-url','value'),
                State('n-pages','value'),
                State('captcha','value'),
                State('captcha-gen','data')])
def get_results(n_clicks,url,n_pages,captcha_result,captcha_gen):

     rew_output=""
     dummy_out=''
     reviews=pd.DataFrame()
     btn_state=False
     if captcha_gen is None:
        captcha_gen={'n1':-50,'n2':0}
     captcha_sum=captcha_gen['n1']+captcha_gen['n2']
     if captcha_result is None:
        captcha_result=-9999
     print(captcha_result,captcha_sum)
     if 'scrp-btn'==ctx.triggered_id and captcha_sum==int(captcha_result):
        #print(url,n_pages)
        n_pages=int(n_pages)
        

        try:

            if n_pages==1:
                res=scrapper.multi_pages(url,n_pages)
            else:
                
                res=scrapper.multi_pages(url,n_pages)
            
            reviews=scrapper.create_yelp_df(res)
            print(reviews)

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
            rew_output=[html.P(' Select rows and you will get some insights.'),html.P("If results don't appear,check your captcha or probably we're blocked due to high usage. Just wait some minutes",style={'width':'50%'}),reviews_data_table]
            btn_state=False
        except Exception as e:
            print(e)
            rew_output="something's wrong, make sure this is a yelp link,check captcha or we have to wait a little bit due to high usage."
     elif captcha_sum!=int(captcha_result):
        rew_output="Check captcha and yelp url"
     else:
        rew_output=""



     return rew_output,reviews.to_json(),dummy_out,btn_state
    
@app.callback(Output('graph-div','children'),
              Output('wordcloud-div','children'),
              Output('text-review','children'),
              Output('text-review','style'),
              [Input({'type':'datatable','index':ALL},'derived_virtual_selected_rows'),
              Input('reviews-store','data')])  
def show_insights(table_index,stored_reviews):
    graph_result=''
    wc_html_img=''
    text_review=''
    test_review_style={'display':'none'}
    try:
        reviews_df=pd.read_json(stored_reviews)
        
        stars=reviews_df.loc[table_index[0][0],'Rating'].split()[0]
        text_review=reviews_df.loc[table_index[0][0],'Review']
        print(text_review)
        graphobj=make_graph(text_review)
        final_content_list=graphobj.clean()
        text_review+=graphic_stars[stars]
        net_style='concentric'
        graph_result=graphobj.render_graph(final_content_list,net_style)
        wc_html_img=graphobj.render_word_cloud(final_content_list)
        test_review_style={'margin-left':'50%','margin-top':'-19%','position':'absolute','overflow':'scroll','height':'50%'}
    except Exception as e:
        print(e)
    
    return graph_result,wc_html_img,text_review,test_review_style







if __name__=='__main__':
    app.run_server(debug=True)
