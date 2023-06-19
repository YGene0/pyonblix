from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import ssl
from urllib.request import urlopen, Request
import requests
from flask_cors import CORS
import math

# SSLContext 생성하여 DH 키 크기 문제 해결
ctx = ssl.create_default_context()
ctx.set_ciphers("DEFAULT@SECLEVEL=1")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_number", methods=["POST"])
def get_number():
    bar = int(request.form["number"].replace(' ', ''))
    print(bar)
    #int(request.form["number"])
    # 알라딘 정보 가져오기
    
    result = []
    url = 'https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=Used&SearchWord=' + str(bar)
    response = urlopen(url, context=ctx)
    soup = BeautifulSoup(response, 'html.parser')
    result2 = soup.select('table.usedtable01')
    try:
        prices = result2[0].find_all('b')
        desired_price = prices[-1].text
        desired_price2 = prices[-2].text
        aladin_p = int(desired_price.strip('원').replace(',', '')) # 개인판매자 가격
        aladin_a = int(desired_price2.strip('원').replace(',', '')) #알라딘 가격
        result.append(min(aladin_a, aladin_p))
    except:
        result.append(0)
    
    url = 'https://www.aladin.co.kr/shop/usedshop/wc2b_search.aspx?ActionType=1&SearchTarget=All&KeyWord=' + str(bar)
    response = urlopen(url, context=ctx)
    soup = BeautifulSoup(response, 'html.parser')
    result2 = soup.select('td.c2b_tablet3')
    booktitle = soup.select('a.c2b_b')
    book_title = booktitle[0].text.strip()
    aladin_1 = int(result2[1].text.strip('원').replace(',', ''))
    aladin_2 = int(result2[2].text.strip('원').replace(',', ''))
    aladin_3 = int(result2[3].text.strip('원').replace(',', ''))
    #print(aladin_1,aladin_2,aladin_3)  #알라딘 최상, 상, 중
    title = book_title
    result.append(aladin_1)
    result.append(aladin_2)
    result.append(aladin_3)
    
    url = 'https://www.yes24.com/Product/Search?domain=USED_GOODS&query=' + str(bar)
    response = Request(url, headers={'User-Agent': 'Mozilla/5.0'})  # User-Agent 설정
    response = urlopen(response, context=ctx)
    soup = BeautifulSoup(response, 'html.parser')
    try:
        result2 = soup.select('em.yes_b')
        yes24_p = int(result2[0].text.replace(',', '')) #예스24 중고가
    except:
        yes24_p = 0
    result.append(yes24_p)
    
    url = 'https://www.yes24.com/Mall/buyback/Search?CategoryNumber=018&SearchWord=' + str(bar)
    response = Request(url, headers={'User-Agent': 'Mozilla/5.0'})  # User-Agent 설정
    response = urlopen(response, context=ctx)
    soup = BeautifulSoup(response, 'html.parser')
    result2 = soup.select('div.bbG_price')
    try:
        table = result2[0].find('table')
        price_data = table.select('tbody tr td')
        yes24_1 = price_data[1].text.strip('원').replace(',', '') #예스24 최상,상,중
        yes24_2 = price_data[2].text.strip('원').replace(',', '')
        yes24_3 = price_data[3].text.strip('원').replace(',', '')
    except:
        yes24_1 = 0
        yes24_2 = 0
        yes24_3 = 0
        
    if yes24_1 == '':
        result.append(0)
    else:
        result.append(yes24_1)
        
    if yes24_2 == '':
        result.append(0)
    else:
        result.append(yes24_2)
        
    if yes24_3 == '':
        result.append(0)
    else:
        result.append(yes24_3)
    
    min_p = int(result[0])
    #min_p = min(int(result[0]), int(result[4]))
    max_1 = max(int(result[1]), int(result[5]))
    max_2 = max(int(result[2]), int(result[6]))
    max_3 = max(int(result[3]), int(result[7]))
    if round(min_p/3,-2) >= max_1:
        real_1 = math.ceil((min_p/3)/100)*100
        if round(max_1*1.1, -2) > round(min_p/3,-2):
            real_1 = math.ceil((max_1*1.1)/100)*100
    elif round(min_p/2,-2) >= round(max_1*1.5,-2):
        real_1 = round(max_1*1.5,-2)
        if math.ceil((min_p/2)/100)*100 >= round(max_1*1.2,-2):
            real_1 = round(max_1*1.2,-2)
    else:
        real_1 = round(min_p/2,-2)
        if math.ceil((min_p/2)/100)*100 >= round(max_1*1.2,-2):
            real_1 = round(max_1*1.2,-2)
        if min_p == 0 and max_1 != 0:
            real_1 = round(max_1*0.65,-2)
    real_2 = math.ceil((real_1*0.9)/100)*100
    real_3 = math.ceil((real_2*0.9)/100)*100
    result.append(real_1)
    result.append(real_2)
    result.append(real_3)
    result.append(title)
        
    print(result)
    
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0")
