import os, os.path
import re
import datetime
import time

import requests
import pandas as pd

from bs4 import BeautifulSoup
from progress.bar import IncrementalBar

catalog = {} # Словарь для хранения данных каталога
category = {} # Словарь для хранения данных категории товара
subcatalog = {} # Словарь для хранения данных подкатегории
right_catalog = ['Овощи и фрукты', 'Молоко, яйца и сыр', 'Сладости и десерты', 'Макароны, крупы и мука', 'Хлеб, выпечка и тесто', 'Диетические продукты', 'Мясо и птица', 'Колбасы и деликатесы', 'Готовая еда', 'Продукция быстрого приготовления', 'Замороженные продукты', 'Рыба и морепродукты', 'Масла и соусы', 
'Приправы и сухие смеси', 'Чай, кофе и какао', 'Напитки', 'Консервация', 'Снеки', 'Детское питание и гигиена', 'Для дома', 'Красота и здоровье']
dictionary = [] # Словарь для поиска товаров по их названию

# Куки и хедер для запроса
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

now = datetime.datetime.now() # Получаем текущую дату и время для последующего названия папки с html кодом всех страниц

# Функция get_catalog для сбора и запись в Excel файл категорий и наименований товаров  
def get_catalog():

    global catalog, category, subcatalog 
    product = {'Каталог': [],'Продукт': [], 'Цена': []} # Создание cловаря товаров

    # Cоздание проверки на происхождение успешного запроса сайта каталога
    success = False
    while not success:
        try:
            response = requests.get('https://yarcheplus.ru/category', cookies=cookies, headers=headers) # Осуществление запроса 
            success = True
        except requests.exceptions.ReadTimeout:
            print('Повторный запрос на сайт Ярче')

    # response = requests.get('https://yarcheplus.ru/category', cookies=cookies, headers=headers)

    if f'Каталог{now.date()}' not in os.listdir(os.getcwd()): # Проверка, существует ли уже файл с названием 'Каталог{Дата ПК}'
        os.mkdir(f'Каталог{now.date()}')

    with open(f'Каталог{now.date()}\\result_catalog.html', 'w', encoding='utf-8') as file: # Создание копии html кода страницы каталога
    	file.write(response.text)

    with open(f'Каталог{now.date()}\\result_catalog.html', 'r', encoding='utf-8') as file: # Чтение копии html кода страницы каталога из файла
        src = file.read()

    soup = BeautifulSoup(src, 'html.parser') # Создание объекта BeautifulSoup из исходного кода HTML

    all_catalog = soup.findAll('div', class_='aF8Dd3Mkw') # Поиск всех тегов каталогов товара
    # all_pages = soup.findAll('div', class_='cHmge+Dmt aCuVgYkar')
    # print(all_pages)

    bar = IncrementalBar('Разделение на каталоги и категории', max = len(all_catalog)) # Создание индикатора выполнения программы
    for name_catalog in all_catalog:
        name = name_catalog.find('a', class_='aex-F4ydD bex-F4ydD').get('href')
        # print(re.search('category', name))
        # print(name)        
        if(re.search('category', name)): # Поиск категории в ссылке используя регулярные выражения
            if name_catalog.text in right_catalog:
                category.update({name_catalog.text: 'https://yarcheplus.ru' + name}) # Добавление в словарь категорий название категории и ссылки
        else:
            if name_catalog.text in right_catalog: 
                catalog.update({name_catalog.text: []})
                catalog[name_catalog.text].append('https://yarcheplus.ru' + name) # Добавление в словарь каталогов название каталогов и ссылки на них
        bar.next()
    bar.finish()

    bar = IncrementalBar('Каталоги', max = len(catalog)) # Создание индикатора выполнения программы
    os.chdir(os.getcwd() + f'\\Каталог{now.date()}')
    for name_catalog, link_catalog in catalog.items():
        response = requests.get(f'{link_catalog[0]}', cookies=cookies, headers=headers) # Запрос на сайт каталога товаров
        soup = BeautifulSoup(response.text, 'html.parser')
        all_pages = soup.select('a.cCuVgYkar:not([class*=" "])') # Поиск пагинатора через CSS-селектор
        # print(name_catalog, all_pages)
        if f'{name_catalog}' not in os.listdir(os.getcwd()): # Проверка на уже существование файла с названием каталога
            os.mkdir(f'{name_catalog}') # Создание папки с названием каталога
        
        with open(f'{name_catalog}\\{link_catalog[0][30:]}.html', 'w', encoding='utf-8') as file: 
            file.write(response.text)
        
        if all_pages: # Условие для прохода страниц каталога, если есть пагинация
            for link_page in all_pages: # Цикл прохода по страницам и записью товаров в словарь product
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
                    price_with_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ lJThHsRzJ gJThHsRzJ aeLALm-u4') # Поиск тега цены без скидки
                    # print(price_with_sale)
                    price_without_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ sJThHsRzJ zJThHsRzJ heLALm-u4') # Поиск тега обычной цены
                    # print(price_without_sale) 
                    if price_with_sale: # Проверка на наличие скидки товара
                        price = price_with_sale.text[:-2].replace(',', '.')
                        # name = name_catalog + ' =======> ' + '!!!Скидка!!!' + name 
                    elif price_without_sale: # Проверка на отсутствие скидки товара
                        price = price_without_sale.text[:-2].replace(',', '.')
                        # name = name_catalog + ' =======> ' + name 

                    # Запись товара в словарь товаров
                    product['Каталог'].append(name_catalog.text)
                    product['Продукт'].append(name)
                    product['Цена'].append(float(price.replace(' ', '')))
        # print(name_catalog, link_catalog)
    # print(os.getcwd())
        bar.next()
    bar.finish()


    bar = IncrementalBar('Категория', max = len(category)) # Создание индикатора выполнения программы
    for name_category, link_category in category.items(): # Цикл прохода по ссылкам категорий
        response = requests.get(f'{link_category}', cookies=cookies, headers=headers)
        if f'{name_category}' not in os.listdir(os.getcwd()): # Проверка на уже существование файла с названием категории
            os.mkdir(f'{name_category}')
        with open(f'{name_category}\\{link_category[31:]}.html', 'w', encoding='utf-8') as file: # Сохранение html кода страницы категории
            file.write(response.text)

        # with open('{0}\\{1}.html'.format('{}'.format(name_category),'{}'.format(link_category[31:])), 'r', encoding='utf-8') as file:
        #     src = file.read()

        soup = BeautifulSoup(response.text, 'html.parser')

        all_catalog = soup.findAll('div', class_='aF8Dd3Mkw')

        for name_subcatalog in all_catalog: # Проход по подкаталогам в категориях товаров
            name = name_subcatalog.find('a', class_='aex-F4ydD bex-F4ydD').get('href')
            subcatalog.update({name_subcatalog.text: []})
            subcatalog[name_subcatalog.text].append('https://yarcheplus.ru' + name)
            
            response_subcatalog = requests.get('https://yarcheplus.ru' + name, cookies=cookies, headers=headers)
            soup = BeautifulSoup(response_subcatalog.text, 'html.parser')
            all_pages = soup.select('a.cCuVgYkar:not([class*=" "])') # Поиск пагинатора подкаталогов через CSS-селектор
            
            # print(name, all_pages)
            # print(os.getcwd() + '\\{}'.format(name_category))
            # print(name_subcatalog.text)
            # print(os.listdir(os.getcwd() + '\\{}'.format(name_category)))

            if f'{name_subcatalog.text}' not in os.listdir(os.getcwd() + f'\\{name_category}'): # Проверка на наличие папки с подкаталога
                os.mkdir('{0}\\{1}'.format(name_category, name_subcatalog.text))

            with open(f'{name_category}\\{name_subcatalog.text}\\{name[9:]}.html', 'w', encoding='utf-8') as file: # Запись html кода подкаталога
                file.write(response_subcatalog.text)

            with open(f'{name_category}\\{name_subcatalog.text}\\{name[9:]}.html', 'r', encoding='utf-8') as file: # Чтение html кода подкаталога
                src = file.read()

            soup = BeautifulSoup(src, 'html.parser')

            all_product = soup.findAll('div', class_='cbU3Ps1qD')
            # print(all_product)
            for name_product in all_product: # Проход всех товаров в подкаталоге 
                name = name_product.find('a', class_='g7Ks4VM+0').text
                # print(re.search('category', name))      
                price_with_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ lJThHsRzJ gJThHsRzJ aeLALm-u4')
                # print(price_with_sale)
                price_without_sale = name_product.find('div', class_='aJThHsRzJ bJThHsRzJ sJThHsRzJ AJThHsRzJ heLALm-u4')
                # print(price_without_sale)
                # print(price_with_sale) 
                if price_with_sale:
                    price = price_with_sale.text[:-2].replace(',', '.')
                    # name = name_subcatalog.text + ' =======> ' + '!!!Скидка!!!' + name 
                elif price_without_sale:
                    price = price_without_sale.text[:-2].replace(',', '.')
                    # name = name_subcatalog.text + ' =======> ' + name 

                product['Каталог'].append(name_subcatalog.text)
                product['Продукт'].append(name)
                product['Цена'].append(float(price.replace(' ', '')))

            if all_pages: # Проверка наличие пагинации в подкаталоге 
                for link_page in all_pages:
                    page = link_page.get('href')
                    subcatalog[name_subcatalog.text].append('https://yarcheplus.ru' + page)
                    response_page = requests.get('https://yarcheplus.ru' + page, cookies=cookies, headers=headers)
                    # print(response_page.text)
                    with open(f'{name_category}\\{name_subcatalog.text}\\{page[9:].replace("?", "#")}.html', 'w', encoding='utf-8') as file: # Запись html кода страницы подкаталога
                        file.write(response_page.text)

                    with open(f'{name_category}\\{name_subcatalog.text}\\{page[9:].replace("?", "#")}.html', 'r', encoding='utf-8') as file: # Чтение html кода страницы подкаталога
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
                            # name = name_subcatalog.text + ' =======> ' + '!!!Скидка!!!' + name 
                        elif price_without_sale:
                            price = price_without_sale.text[:-2].replace(',', '.')
                            # name = name_subcatalog.text + ' =======> ' + name 

                        product['Каталог'].append(name_subcatalog.text)
                        product['Продукт'].append(name)
                        product['Цена'].append(float(price.replace(' ', '')))
        bar.next()
    bar.finish()

    df = pd.DataFrame(product) # Создание таблицы с рядами и столбцами 
    df.drop_duplicates(subset=['Продукт'], inplace=True) # Удаление дубликатов
    df.to_excel(f'C:\\Users\\User\\Desktop\\Творческий\\Каталог{now.date()}\\product.xlsx', index=False) # Создание эксель файла 
    # print(os.getcwd())
    # print("==============")
    # print(subcatalog)
    # print("==============")
    # print(category)
    # print("==============")
    # print(catalog)    


def main():
    get_catalog()

if __name__ == '__main__':
    main()