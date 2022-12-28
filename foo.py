# sys.argv <- 
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup 
from tqdm import tqdm
import time
import datetime

d_today = datetime.date.today() # 오늘 날짜

#!pip install --upgrade pip
#!pip install JPype1
#!pip install konlpy
import numpy as np
from konlpy.tag import Okt 
from konlpy.tag import Kkma 
from threading import Thread
from konlpy.tag import Twitter
from collections import Counter

import jpype

###

import matplotlib.pyplot as plt
from pdf_reports import JupyterPDF
from IPython.display import display_html
from pdf_reports import pug_to_html, write_report

#search_word= '고구려말기' # input word -> init 
def func_1(x):    
    return r'<a href={}>링크</a>'.format(x)

def func_2(x):
    return x.split(',')[0]

def KCI(x):
    x_list = []
    for i in range(len(x)): 
        x_list.append(x[i]['alt'])
    if x_list == [] : 
        x_list = ['학술논문']
    return x_list

pg = \
'''
h1 논문 검색 결과 

#sidebar: p Medbiz 논문 검색 결과를 바탕으로 만들어진 PDF 보고서 입니다. 

{{ pdf_tools.dataframe_to_html(dataframe) }}

<style> h3 {margin-top: 4em;} </style>
'''

def number_to_string(dayOfWeek):
    switcher = {
        "최신순" : "DATE",
        "조회도순": "VIEWCOUNT",
        "랭킹순": "RANK",
    }
    return switcher.get(dayOfWeek, "nothing")


class service_crawl(): 
    
    def __init__(self): # 정렬 
        # sys.argv[1], sys.argv[2] , sys.argv[3], sys.argv[4], sys.argv[5]
        self.input_word_1 = sys.argv[1]
        self.input_word_2 = sys.argv[2]
        self.search_word = self.input_word_1 + ' ' + self.input_word_2
        self.sort_value = sys.argv[3]
        self.number_page = sys.argv[4]
        self.start_point = sys.argv[5]
        self.save_point  = sys.argv[6]
        self.pg = pg
        # 정렬
        # 경로 input 
        # 경로 output

    def count_page(self):
      
        total_url = "http://www.riss.kr/search/Search.do?isDetailSearch=N&searchGubun=true&viewYn=OP&query=%s&queryText=&iStartCount=%d&iGroupView=5&icate=all&colName=re_a_kor&exQuery=&exQueryText=&order=%s&onHanja=false&strSort=RANK&pageScale=10&orderBy=&fsearchMethod=search&isFDetailSearch=N&sflag=1&searchQuery=%s&fsearchSort=&fsearchOrder=&limiterList=&limiterListText=&facetList=&facetListText=&fsearchDB=&resultKeyword=%s&pageNumber=1&p_year1=&p_year2=&dorg_storage=&mat_type=&mat_subtype=&fulltext_kind=&t_gubun=&learning_type=&language_code=&ccl_code=&language=&inside_outside=&fric_yn=&image_yn=&regnm=&gubun=&kdc=&ttsUseYn="%(self.search_word,0,"%2FDESC",self.search_word, self.search_word )
        total_req = requests.get(total_url)
        total_html = total_req.text
        soup = BeautifulSoup(total_html, 'html.parser') # 파싱 라이브러리 
        total_tag = soup.select("#divContent > div > div.rightContent.wd756 > div > div.searchBox > dl > dd > span > span") # 

        total_page= round(int(total_tag[0].text.replace(",",""))/10) # 하위 자식태그의 텍스트까지 문자열로 반환
        return total_page
    
    def crawl_main(self): 

        count = 0 
         
        # 검색 페이지 수 입력
        # 음수, 숫자 아닌 값에 대한 대안 추가 -> ui 단에서 처리

        total = service_crawl.count_page(self)

        if total ==0: # input number
            num = 1
        elif int(self.number_page) > int(total) :
            num = int(total) # count_page(search_word)
        else : 
            num = int(self.number_page)

        
        for q in (range(num)): # tqdm
            #time.sleep(5) #자는 코드

            
            
            url = "http://www.riss.kr/search/Search.do?isDetailSearch=N&searchGubun=true&viewYn=OP&query=%s&queryText=&iStartCount=%d&iGroupView=5&icate=all&colName=re_a_kor&exQuery=&exQueryText=&order=%s&onHanja=false&strSort=%s&pageScale=10&orderBy=&fsearchMethod=search&isFDetailSearch=N&sflag=1&searchQuery=%s&fsearchSort=&fsearchOrder=&limiterList=&limiterListText=&facetList=&facetListText=&fsearchDB=&resultKeyword=%s&pageNumber=1&p_year1=&p_year2=&dorg_storage=&mat_type=&mat_subtype=&fulltext_kind=&t_gubun=&learning_type=&language_code=&ccl_code=&language=&inside_outside=&fric_yn=&image_yn=&regnm=&gubun=&kdc=&ttsUseYn="%(self.search_word, q*10, "%2FDESC" ,number_to_string(self.sort_value) ,self.search_word, self.search_word )
            # %(self.search_word,q*10,"%2FDESC",self.search_word, self.search_word 
            req = requests.get(url)
            html = req.text
            #print("%d페이지를 가져옴"%(q+1))
            globals()['df{}'.format(q)] = pd.DataFrame()
            soup = BeautifulSoup(html, 'html.parser') 
            title_tag = soup.select("div.cont.ml60 > p.title > a")                            # 제목
            writer_tag = soup.select("div.cont.ml60 > p.etc > span.writer")               # 저자
            assigned_tag = soup.select("div.cont.ml60 > p.etc > span.assigned")           # 발행기관
            journal_tag = soup.select("div.cont.ml60 > p.etc > span:nth-child(4) > a")    # 학술지명
            agency_tag = soup.select("div.cont.ml60 > p.etc > span:nth-child(3)")         # 발행년도
            vo_tag = soup.select("div.cont.ml60 > p.etc > span:nth-child(5)")             # 권호사항
            href_tag = soup.select("div.cont.ml60 > p.title > a")             # 권호사항
            title_list = [] 
            writer_list = [] 
            assigned_list = [] 
            journal_list = [] 
            agency_list = [] 
            vo_list = []
            href_list =[]
            green_list  = []
            register_list = []

            for i in range(len(title_tag)):
                title_list.append(title_tag[i].text)

                try : writer_list.append(writer_tag[i].text)
                except : writer_list.append("")

                #register_list.append(register(soup.select("ul > li:nth-child(%d) > div.markW > span > img"%(i+1) ) == []))
                register_list.append(KCI(soup.select("ul > li:nth-child(%d) > div.markW > span > img"%(i+1) )))

                assigned_list.append(assigned_tag[i].text)
                journal_list.append(journal_tag[i].text)
                agency_list.append(agency_tag[i].text)

                try : vo_list.append(vo_tag[i].text)
                except : vo_list.append("")

                href_list.append("http://www.riss.kr" + href_tag[i].get("href"))
                j = i+1
                                                                                    # 초록 추가
                green_tag = soup.select("li:nth-child(%d) > div.cont.ml60 > p.preAbstract"%j)
                try :
                    green_list.append(green_tag[0].text)
                except :
                    green_list.append("-")

            globals()['df{}'.format(q)]['제목'] = title_list
            globals()['df{}'.format(q)]['저자'] = writer_list
            
            globals()['df{}'.format(q)]['등재여부'] = register_list  # 등재여부 추가 
            globals()['df{}'.format(q)]['발행기관'] = assigned_list
            globals()['df{}'.format(q)]['학술지명'] = journal_list
            globals()['df{}'.format(q)]['발행년도'] = agency_list
            globals()['df{}'.format(q)]['권호사항'] = vo_list
            globals()['df{}'.format(q)]['링크'] = href_list
            globals()['df{}'.format(q)]['초록'] = green_list
            #print('-- 데이터프레임 만들기 --')
            prev =  globals()['df{}'.format(q)]
            try:
                last = pd.concat( [ last, prev] , axis =0 )
                #print('-- 데이터프레임 합치기 --')
            except:
                last = globals()['df{}'.format(q)]

        df_last = last.reset_index(drop=True)
        df_replaced = df_last.replace([], '')

        df_test = pd.DataFrame(columns=['대분류', '소분류' ,'제목', '년도', '저자', '구분', '등재'])#,'저자',  '요약', '링크'])

        df_test['제목'] = df_replaced.제목.values
        df_test['년도'] = df_replaced.발행년도.values
        df_test['저자'] = df_replaced.저자.values
        df_test['등재'] = df_replaced.등재여부.values
        #df_test['요약'] = df_replaced.초록.values
        #df_test['검색어'] = search_word
        df_test['대분류'] = self.input_word_1
        df_test['소분류'] = self.input_word_2

        df_test['링크'] = df_replaced.링크.apply(func_1).values
        df_test['저자'] = df_test['저자'].apply(func_2)
        
        ndarray_name = df_replaced.제목.values
        ndarray_green = df_replaced.초록.values

        for i in range(len(df_test['등재'])):
            df_test['등재'][i] = ','.join(df_test['등재'][i])

        df_test['구분'] = "논문"
        df_test = df_test.replace('', np.nan)
        #df_test = df_test.dropna(axis = 0)
        return df_test 
    
    def pdf_page(self): # 경로설정
        
        
        f = open( self.start_point + '/' + "test.pug", 'w')
        f.write(self.pg)
        f.close()
        
        html = pug_to_html("test.pug", dataframe=service_crawl.crawl_main(self))
        #print(len(service_crawl.crawl_main(self)))
        write_report(html, self.save_point + '/' + "pdf_report.pdf")
        #JupyterPDF("pdf_report.pdf")
    
    
    def crawl(self):
        #print('검색어 : ' , self.search_word)
        #print('정렬 : @@@@ ')
        #print('모든 페이지 수 : ' ,service_crawl.count_page(self))
        print(self.sort_value)
        service_crawl.pdf_page(self)
        
def main():
    p1 = service_crawl() # sys.argument
    p1.crawl() # 합치고 정렬 후에 pdf로 저장 or 따로 구분지어 나오게 저장 
    
if __name__ == "__main__":
    main()