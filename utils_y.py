import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from dash import Dash, dcc, html
import re
import nltk
import pandas as pd
import dash_cytoscape as cyto

from PIL import Image
from wordcloud import WordCloud
import base64
from io import BytesIO

import string

class yelp_scrapper:
    
        

    def get_yelp_reviews(self,url):
        reviews=[]
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html')
        for EachPart in soup.select('div[class*="review__"]'):
            review=BeautifulSoup(str(EachPart.select('span[class*="raw__"]')),'html')
            star=BeautifulSoup(str(EachPart.select('div[class*="five-stars__"]')[0]),'html')
            for i  in review.select('span[class*="raw__"]'):
                reviews.append([i.get_text(),star.find_all('div')[0].attrs['aria-label']])
        
            
        return reviews

    def multi_pages(self,url,n):
        
        if n>1:
            
        
            return [f'{url}?start={10*i}' if i>0 else url for i in range(n+1) ]
        else:
            return [url]

    def create_yelp_df(self,url_list):

        df_reviews=pd.DataFrame()
        total_reviews=[]
        for url in url_list:
            total_reviews+=self.get_yelp_reviews(url)
            time.sleep(0.5)
            #print(self.get_yelp_reviews(url))
        df_reviews=pd.DataFrame(total_reviews)
        df_reviews=df_reviews.rename(columns={0:'Review',1:'Rating'})
        

        return df_reviews

class make_graph:
    def __init__(self,content,language='eng'):
        self.content=content
        self.language=language
        
    
    def clean(self):
        self.content=self.content.strip()
        
        if self.language=='eng':
            cleaned=re.sub('[^A-Za-z0-9]+',' ',self.content)
            cleaned=self.content.translate(str.maketrans('','',string.punctuation))
            
            nltk.download('wordnet')
            stopwords_list=stopwords.words('english')
            wnl = WordNetLemmatizer()
            content_list=cleaned.split()
           
            content_list=[i.lower() for i in content_list]
            content_list=[i for i in content_list if i not in stopwords_list]
            final_content_list=[wnl.lemmatize(w) for w in content_list]
               
        #final_content_list=[i for i in new_content_list if i not in stopwords_list]
        final_content_list=[i for i in final_content_list if i!=' ']
        print(final_content_list)
        return final_content_list


    def render_graph(self,final_content_list,style_param='random',max_words='all'):       
        
        
        
        df=pd.DataFrame({'words':final_content_list})
        count_df=df['words'].value_counts()
        if max_words=='all':
            print('todos')
            nodes=list(count_df.index)
        else:
            print('nums')
            nodes=list(count_df.index[:int(max_words)])

        #dict_nodes={w:i+1 for i,w in enumerate(nodes)}
        df=df[df['words'].isin(nodes)]
        #df['num']=df['words'].apply(lambda x: dict_nodes[x])
        df['idx']=[i for i in range(1,len(df)+1)]
        df=df.set_index('idx')
        nodes=[{'data':{'id':df.loc[i,'words'],'label':df.loc[i,'words']}} for i in df.index]
        edges=[]
        for i in df.index:
            if i+1<df.index[-1]:
                source=df.loc[i,'words']
                target=df.loc[i+1,'words']
                if source!=target:
                    edges.append({'data':{'source':source,'target':target}})
        complete_graph=nodes+edges

        graphobj=cyto.Cytoscape(id='grafo',
            layout={'name':f'{style_param}'},
            style={'width': '50%', 'height': '500px'},
            elements=complete_graph,
            stylesheet=[{
                'selector': 'label',             # as if selecting 'node' :/
                'style': {
                    'content': 'data(label)',    # not to loose label content
                    'color': 'black',
                    'background-color': '#537FE7',
                    'line-color':'light-gray'  # applies to node which will remain pink if selected :/
                 }
            }]
        )
        return graphobj
    def render_word_cloud(self,final_content_list):
        wordcloud = WordCloud(background_color='white').generate(' '.join(final_content_list))
        wc_img = wordcloud.to_image()
        with BytesIO() as buffer:
            wc_img.save(buffer, 'png')
            img2 = base64.b64encode(buffer.getvalue()).decode()
        return html.Img(src="data:image/png;base64," + img2)


