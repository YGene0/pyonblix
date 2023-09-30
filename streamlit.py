import streamlit as st
import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import requests

total_title_info = []
title_list = []
etc_info_list = []
price_list = []
img_list = []
cart_img = []
cart_title = []
cart_etc_info = []
cart_price = []

def scrapping(input_search):
    bar = input_search
    url = 'https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=Book&KeyWord=' + bar.replace(' ', '+') #+ '&page=2'
    response = requests.get(url)
    html_data = response.text
    #response = urlopen(url, context=ctx)
    soup = BeautifulSoup(html_data, 'html.parser')

    for link in soup.find_all('img'):
        info = link.get('src').split('/')
        if 'product' in info:
            img_list.append(link.get('src'))

    prices = soup.find_all('span', class_='')
    for price in prices:
        numeric_price = ''.join(filter(lambda x: x.isdigit() or x == ',', price.text))
        if numeric_price and ',' in numeric_price:
            cleaned_price = numeric_price.replace(',', '')
            if cleaned_price:
                price_list.append(int(cleaned_price))
    if price_list[0] == 3:
        del price_list[0]

    for link in soup.find_all('li'):
        total_title_info.append(link.text)
        if '[국내도서]' in link.text:
            title_list.append(link.text.replace('[국내도서]',''))
    for a in range(len(total_title_info)):
        if '[국내도서]' in total_title_info[a]:
            etc_info_list.append(total_title_info[a+1])

    if len(img_list) > len(price_list)/2:
        del img_list[0]
        
    return title_list, etc_info_list, img_list, price_list
   
def main():
    # Initialize session_state
    if "title_list" not in st.session_state:
        st.session_state.title_list = []
    if "etc_info_list" not in st.session_state:
        st.session_state.etc_info_list = []
    if "img_list" not in st.session_state:
        st.session_state.img_list = []
    if "price_list" not in st.session_state:
        st.session_state.price_list = []
    if "cart_title" not in st.session_state:
        st.session_state.cart_title = []
    if "cart_etc_info" not in st.session_state:
        st.session_state.cart_etc_info = []
    if "cart_img" not in st.session_state:
        st.session_state.cart_img = []
    if "cart_price" not in st.session_state:
        st.session_state.cart_price = []

    with st.sidebar:
        st.write('이용방법')
        st.write('장바구니')
        st.write('문의하기')
    
    tab1, tab2 = st.tabs(['검색','장바구니'])
    with tab1:
        st.title("PyonBlix 도서 검색")
        query = st.text_input("구매하시고 싶은 도서 이름을 입력해주세요.")
        if st.button('검색'):
            empty1, spinner, empty2 = st.columns([4,2,4])
            with spinner:
                with st.spinner("검색중.."):
                    title_list, etc_info_list, img_list, price_list = scrapping(query)
                    st.session_state.title_list = title_list
                    st.session_state.etc_info_list = etc_info_list
                    st.session_state.img_list = img_list
                    st.session_state.price_list = price_list

        for a in range(len(st.session_state.img_list)):
            with st.container():
                info1, info2, info3 = st.columns([2,8,3])
                with info1:
                    st.image(st.session_state.img_list[a])
                with info2:
                    st.subheader(st.session_state.title_list[a])
                    st.write(st.session_state.etc_info_list[a])
                with info3:
                    st.write('정가: ', st.session_state.price_list[2*a], '원')
                    st.write('판매가: ',int(st.session_state.price_list[2*a]/2),'원')
                    if st.button('장바구니 담기', key=a):
                        st.session_state.cart_title.append(st.session_state.title_list[a])
                        st.session_state.cart_etc_info.append(st.session_state.etc_info_list[a])
                        st.session_state.cart_img.append(st.session_state.img_list[a])
                        st.session_state.cart_price.append(st.session_state.price_list[2*a])

    with tab2:
        st.title('장바구니')
        empty0, refresh, del_all = st.columns([6,2,1.5])
        with refresh:
            st.button('주문서 생성')
        with del_all:
            st.button('비우기')
        for i in range(len(st.session_state.cart_img)):
            with st.container():
                info1, info2, info3 = st.columns([2,8,3])
                with info1:
                    st.image(st.session_state.cart_img[i])
                with info2:
                    st.subheader(st.session_state.cart_title[i])
                    st.write(st.session_state.cart_etc_info[i])
                with info3:
                    st.write('정가: ', st.session_state.cart_price[i], '원')
                    st.write('판매가: ',int(st.session_state.cart_price[i]/2),'원')
                    st.button('삭제', key=i+1000)
    
            
        
if __name__ == "__main__":
    main()