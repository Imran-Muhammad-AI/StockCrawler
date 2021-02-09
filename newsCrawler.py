## changes for test commit

from lxml.html import parse
from pandas.io.parsers import TextParser
from urllib.request import urlopen
import urllib
import requests
from lxml import html
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
import re
import time

class newsCrawler:
    def __init__(self):
        url = 'https://www.prnewswire.com/news-releases/news-releases-list/'
        hdr = {'User-Agent':'Mozilla/5.0'}
        self.stockSymbol=['TSE','TSX','NSE:','NYSE','TSXV:']

        req = urllib.request.Request(url,headers=hdr)
        page = urlopen(req)
        docTree = parse(page)
        doc = docTree.getroot()
        
        self._persistentDF= pd.read_csv('news.csv') 
        self._currentDF=pd.DataFrame(columns =['stock_symbol', 'News_content','Heading','TIme','DateNews'])
        print(self._currentDF)
        self.lDataforViz = []
        
    ### converting div to dataframe
    def getNews(self,parent):
        d={}
        l=[]
        uniqueList=[]

        strp=str(parent.text_content())       

        for element in parent.iter():
            d.update({element.tag : element.text})

        ## change this later - pass stock tickers
        lstofSymbol = re.findall(r"\(((?:TSX|TSXV|NSE|TSE|NYSE)[:A-Za-z0-9_\s-]+)",  strp)
        l.extend(lstofSymbol)

        ## remove duplicates from list
        [uniqueList.append(x) for x in l if x not in uniqueList] 
        d.update({'listofsymbol' : uniqueList , 'DateNews':pd.to_datetime('today').date()})

        return d
    
    def isRowAlreadyProcessed(self,Cval,currentDF):
        df=currentDF.loc[currentDF['Heading'] == Cval]
        return not df.empty
        
    ##stockSymbol=['TSE','BSE','NSE:','NYSE','TSXV:']
    def FindAllNews(self,liststockSymbol):
        url = 'https://www.prnewswire.com/news-releases/news-releases-list/'
        hdr = {'User-Agent':'Mozilla/5.0'}
        req = urllib.request.Request(url,headers=hdr)
        page = urlopen(req)
        docTree = parse(page)
        doc = docTree.getroot()
        currentDF=pd.DataFrame(columns =['stock_symbol', 'News_content','Heading','TIme','DateNews'])

        dic={}
        allData=[]
        df=pd.DataFrame()

        ##find all parents elements
        for s in liststockSymbol:
            kind=s
            Htmltags = docTree.xpath('.//*[contains(text(),"%s")]' % kind)
            listofDivs=[h.getparent() for h in Htmltags]

            ## create a list of dictionaries , 1 for each div element
            for div in listofDivs:
                allData.append(self.getNews(div))
                
            # dataframe from list of dictionaries
            ## ignore_index=True
            currentDF.append(allData,ignore_index=True) 
               
        return currentDF
    
    def getSymbolsfromNews(self):
        
        lDataforViz=[]        
        currDF= self.FindAllNews(self.stockSymbol)
        
        for index, row in currDF.iterrows():
            print(type(row))
            if(isRowAlreadyProcessed(row['Heading'])):
                continue
            for s in row['listofsymbol'] :
                ##yahooDF = yahoo_finance_df(s.split()[1])
                lDataforViz.append(yahoo_finance_df(s.split()[1]))
                ##displayVisualization(lDataforViz)
                
        return lDataforViz
    
    def displayVisualization(self,listforViz,kplots=4):    
        if len(listforViz) > kplots:
            listforViz.pop(0)
        ### display plot
        ts_plot(listforViz, xlabel='Time', ylabel='Observed Quantity', title='Time Series', height=4, width=10)
        
                
    def ts_plot(self,X, xlabel='Time', ylabel='Observed Quantity', title='Time Series', height=4, width=10):
        fig, ax = plt.subplots(figsize=(width, height))
        markers = ['*', '.', 'o', '^']
        colors = ['b', 'r', 'g', 'y']
        # Add x-axis and y-axis
        for i, xi in enumerate(X):
            xi.plot(ax=ax, linestyle='-', marker=markers[i], color=colors[i])
            # Set title and labels for axes
        ax.set(xlabel=xlabel,ylabel=ylabel,title=title)
        if len(X) > 1: # more than one series
            ax.legend()
        plt.show()
        
    def yahoo_finance_df(self,stockTicker):     
        url = 'http://finance.yahoo.com/q/op?s={}+Options'.format(stockTicker)
        page = urlopen(url)
        parsed = parse(page)
        doc = parsed.getroot()

        tables = doc.findall('.//table')
        df = parse_options_data(tables[0])
        df= df.replace(to_replace=["?","-",",", ";"], value=np.nan)
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

        return df
    
    ## parsing table    
    def parse_options_data(self,table):
        rows = table.findall('.//tr')
        header = _unpack(rows[0], kind='th')
        data = [_unpack(r) for r in rows[1:]]
        print(len(data))
        print(type(data))  
        return TextParser(data, names=header).get_chunk()
    
    ## row data
    def _unpack(self,row, kind='td'):
        elts = row.findall('.//%s' % kind)
        return [str(val.text_content()) for val in elts]
    
    ## is this row not yet processed today
    def isAlreadyProcessed(self,fullDF,currentDF):
        df = currentDF.merge(fullDF, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='left_only']
        return df
        

def main():
        n=newsCrawler()
        dataSymbols = n.getSymbolsfromNews()
        print(dataSymbols)

if __name__ == "__main__":
        main()
        #print("Guru99")