import requests
from bs4 import BeautifulSoup
import pandas as pd

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
            #print(self.get_yelp_reviews(url))
        df_reviews=pd.DataFrame(total_reviews)
        df_reviews=df_reviews.rename(columns={0:'Review',1:'Rating'})
        

        return df_reviews


