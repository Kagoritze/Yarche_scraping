import os, os.path
import re
import datetime
import time

import requests
import pandas as pd

from bs4 import BeautifulSoup
from progress.bar import IncrementalBar

catalog = {}
category = {}
subcatalog = {}
slovar = []

cookies = {
    'tmr_lvid': '1e13183d26e1a3265735f6fd98e20a61',
    'tmr_lvidTS': '1676286803846',
    '_ym_uid': '1676286804771721358',
    '_ym_d': '1676286804',
    'cookieBannerShowed': 'true',
    'token': '900e11ebe7dc643822a522f8cac30080e32ce228-90dee971c58cd91000a562356b54d79fb0af0d80',
    'refresh-token': '14afcf3f62c489bf795a9b8e15a34e7b25486c71-5b4f35dae627acaaac604bb4bd63b41328467f47',
    '_ym_isad': '1',
    '_ym_visorc': 'w',
    'tmr_detect': '1%7C1677425069300',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Cookie': 'tmr_lvid=1e13183d26e1a3265735f6fd98e20a61; tmr_lvidTS=1676286803846; _ym_uid=1676286804771721358; _ym_d=1676286804; cookieBannerShowed=true; token=900e11ebe7dc643822a522f8cac30080e32ce228-90dee971c58cd91000a562356b54d79fb0af0d80; refresh-token=14afcf3f62c489bf795a9b8e15a34e7b25486c71-5b4f35dae627acaaac604bb4bd63b41328467f47; _ym_isad=1; _ym_visorc=w; tmr_detect=1%7C1677425069300',
    'Pragma': 'no-cache',
    'Referer': 'https://www.google.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

now = datetime.datetime.now()

def get_catalog():

    global catalog, category, subcatalog
    product = {'Продукт': [], 'Цена': []}

    success = False
    while not success:
        try:
            response = requests.get('https://yarcheplus.ru/category', cookies=cookies, headers=headers)
            success = True
        except requests.exceptions.ReadTimeout:
            print('Повторный запрос на сайт Ярче')

    # response = requests.get('https://yarcheplus.ru/category', cookies=cookies, headers=headers)

    if f'Каталог{now.date()}' not in os.listdir(os.getcwd()):
        os.mkdir(f'Каталог{now.date()}')

    with open(f'Каталог{now.date()}\\result_catalog.html', 'w', encoding='utf-8') as file:
    	file.write(response.text)

    with open(f'Каталог{now.date()}\\result_catalog.html', 'r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'html.parser')

    all_catalog = soup.findAll('div', class_='aF8Dd3Mkw')
    # all_pages = soup.findAll('div', class_='cHmge+Dmt aCuVgYkar')
    # print(all_pages)

    bar = IncrementalBar('Разделение на каталоги и категории', max = len(all_catalog))
    for name_catalog in all_catalog:
        name = name_catalog.find('a', class_='aex-F4ydD bex-F4ydD').get('href')
        # print(re.search('category', name))
        # print(name)        
        
        if(re.search('category', name)):
            category.update({name_catalog.text: 'https://yarcheplus.ru' + name})
        else:
            catalog.update({name_catalog.text: []})
            catalog[name_catalog.text].append('https://yarcheplus.ru' + name)
        bar.next()
    bar.finish()
         

    bar = IncrementalBar('Каталоги', max = len(catalog))
    os.chdir(os.getcwd() + f'\\Каталог{now.date()}')
    for name_catalog, link_catalog in catalog.items():
        response = requests.get(f'{link_catalog[0]}', cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        all_pages = soup.select('a.cCuVgYkar:not([class*=" "])') #CSS-селектор
        # print(name_catalog, all_pages)
        if f'{name_catalog}' not in os.listdir(os.getcwd()):
            os.mkdir(f'{name_catalog}')
        
        with open(f'{name_catalog}\\{link_catalog[0][30:]}.html', 'w', encoding='utf-8') as file:
                file.write(response.text)
        if all_pages:
            for link_page in all_pages:
                page = link_page.get('href')
                catalog[name_catalog].append('https://yarcheplus.ru' + page)
                response_page = requests.get('https://yarcheplus.ru' + page, cookies=cookies, headers=headers)
                # print(response_page.text)
                with open(f'{name_catalog}\\{page[9:].replace("?", "#")}.html', 'w', encoding='utf-8') as file:
                    file.write(response_page.text)
                with open(f'{name_catalog}\\{page[9:].replace("?", "#")}.html', 'r', encoding='utf-8') as file:
                    src = file.read()
                soup = BeautifulSoup(src, 'html.parser')

                all_product = soup.findAll('div', class_='cbU3Ps1qD')
                # print(all_product)
                for name_product in all_product:
                    name = name_product.find('a', class_='g7Ks4VM+0').text
                    # print(re.search('category', name))      
                    price_with_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ lJThHsRzJ gJThHsRzJ aeLALm-u4')
                    # print(price_with_sale)
                    price_without_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ sJThHsRzJ zJThHsRzJ heLALm-u4')
                    # print(price_without_sale) 
                    if price_with_sale:
                        price = price_with_sale.text[:-2].replace(',', '.')
                        name = name_catalog + ' =======> ' + '!!!Скидка!!!' + name 
                    elif price_without_sale:
                        price = price_without_sale.text[:-2].replace(',', '.')
                        name = name_catalog + ' =======> ' + name 

                    product['Продукт'].append(name)
                    product['Цена'].append(float(price.replace(' ', '')))
        # print(name_catalog, link_catalog)
    # print(os.getcwd())
        bar.next()
    bar.finish()


    bar = IncrementalBar('Категория', max = len(category))
    for name_category, link_category in category.items():
        response = requests.get(f'{link_category}', cookies=cookies, headers=headers)
        if f'{name_category}' not in os.listdir(os.getcwd()):
            os.mkdir(f'{name_category}')
        with open(f'{name_category}\\{link_category[31:]}.html', 'w', encoding='utf-8') as file:
            file.write(response.text)

        # with open('{0}\\{1}.html'.format('{}'.format(name_category),'{}'.format(link_category[31:])), 'r', encoding='utf-8') as file:
        #     src = file.read()

        soup = BeautifulSoup(response.text, 'html.parser')

        all_catalog = soup.findAll('div', class_='aF8Dd3Mkw')

        for name_subcatalog in all_catalog:
            name = name_subcatalog.find('a', class_='aex-F4ydD bex-F4ydD').get('href')
            subcatalog.update({name_subcatalog.text: []})
            subcatalog[name_subcatalog.text].append('https://yarcheplus.ru' + name)
            
            response_subcatalog = requests.get('https://yarcheplus.ru' + name, cookies=cookies, headers=headers)
            soup = BeautifulSoup(response_subcatalog.text, 'html.parser')
            all_pages = soup.select('a.cCuVgYkar:not([class*=" "])') #CSS-селектор
            
            # print(name, all_pages)
            # print(os.getcwd() + '\\{}'.format(name_category))
            # print(name_subcatalog.text)
            # print(os.listdir(os.getcwd() + '\\{}'.format(name_category)))

            if f'{name_subcatalog.text}' not in os.listdir(os.getcwd() + f'\\{name_category}'):
                os.mkdir('{0}\\{1}'.format(name_category, name_subcatalog.text))

            with open(f'{name_category}\\{name_subcatalog.text}\\{name[9:]}.html', 'w', encoding='utf-8') as file:
                file.write(response_subcatalog.text)

            with open(f'{name_category}\\{name_subcatalog.text}\\{name[9:]}.html', 'r', encoding='utf-8') as file:
                src = file.read()
            soup = BeautifulSoup(src, 'html.parser')

            all_product = soup.findAll('div', class_='cbU3Ps1qD')
            # print(all_product)
            for name_product in all_product:
                name = name_product.find('a', class_='g7Ks4VM+0').text
                # print(re.search('category', name))      
                price_with_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ lJThHsRzJ gJThHsRzJ aeLALm-u4')
                # print(price_with_sale)
                price_without_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ sJThHsRzJ zJThHsRzJ heLALm-u4')
                # print(price_without_sale) 
                if price_with_sale:
                    price = price_with_sale.text[:-2].replace(',', '.')
                    name = name_subcatalog.text + ' =======> ' + '!!!Скидка!!!' + name 
                elif price_without_sale:
                    price = price_without_sale.text[:-2].replace(',', '.')
                    name = name_subcatalog.text + ' =======> ' + name 

                product['Продукт'].append(name)
                product['Цена'].append(float(price.replace(' ', '')))

            if all_pages:
                for link_page in all_pages:
                    page = link_page.get('href')
                    subcatalog[name_subcatalog.text].append('https://yarcheplus.ru' + page)
                    response_page = requests.get('https://yarcheplus.ru' + page, cookies=cookies, headers=headers)
                    # print(response_page.text)
                    with open(f'{name_category}\\{name_subcatalog.text}\\{page[9:].replace("?", "#")}.html', 'w', encoding='utf-8') as file:
                        file.write(response_page.text)

                    with open(f'{name_category}\\{name_subcatalog.text}\\{page[9:].replace("?", "#")}.html', 'r', encoding='utf-8') as file:
                        src = file.read()
                    soup = BeautifulSoup(src, 'html.parser')

                    all_product = soup.findAll('div', class_='cbU3Ps1qD')
                    # print(all_product)
                    for name_product in all_product:
                        name = name_product.find('a', class_='g7Ks4VM+0').text
                        # print(re.search('category', name))      
                        price_with_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ lJThHsRzJ gJThHsRzJ aeLALm-u4')
                        # print(price_with_sale)
                        price_without_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ sJThHsRzJ zJThHsRzJ heLALm-u4')
                        # print(price_without_sale) 
                        if price_with_sale:
                            price = price_with_sale.text[:-2].replace(',', '.')
                            name = name_subcatalog.text + ' =======> ' + '!!!Скидка!!!' + name 
                        elif price_without_sale:
                            price = price_without_sale.text[:-2].replace(',', '.')
                            name = name_subcatalog.text + ' =======> ' + name 

                        product['Продукт'].append(name)
                        product['Цена'].append(float(price.replace(' ', '')))
        bar.next()
    bar.finish()

    df = pd.DataFrame(product)
    df.to_excel(f'C:\\Users\\User\\Desktop\\Творческий\\Каталог{now.date()}\\product.xlsx', index=False)
    # print(os.getcwd())
    # print("==============")
    # print(subcatalog)
    # print("==============")
    # print(category)
    # print("==============")
    # print(catalog)

def get_product():
    pass


def main():
    get_catalog()
    get_product()

if __name__ == '__main__':
    main()