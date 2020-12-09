import requests
from glob import glob
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# http://www.networkinghowtos.com/howto/common-user-agent-list/
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


def search_product_list(interval_count = 1, interval_hours = 6):
   
    prod_tracker = pd.read_csv('takip/urunler.csv', sep=';')
    prod_tracker_URLS = prod_tracker.url
    tracker_log = pd.DataFrame()
    now = datetime.now().strftime('%Y-%m-%d %Hh%Mm')
    interval = 0 # sayacı sıfırla
    
    while interval < interval_count:

        for x, url in enumerate(prod_tracker_URLS):
            page = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(page.content, features="lxml")
            
            #Ürün adı
            title = soup.find(id='productTitle').get_text().strip()
            
            
            try:
                price = float(soup.find(id='priceblock_ourprice').get_text().replace('.', '').replace('€', '').replace(',', '.').strip())
            except:
                try:
                    price = float(soup.find(id='priceblock_saleprice').get_text().replace('$', '').replace(',', '').strip())
                except:
                    price = ''

            try:
                review_score = float(soup.select('i[class*="a-icon a-icon-star a-star-"]')[0].get_text().split(' ')[0].replace(",", "."))
                review_count = int(soup.select('#acrCustomerReviewText')[0].get_text().split(' ')[0].replace(".", ""))
            except:
                try:
                    review_score = float(soup.select('i[class*="a-icon a-icon-star a-star-"]')[1].get_text().split(' ')[0].replace(",", "."))
                    review_count = int(soup.select('#acrCustomerReviewText')[0].get_text().split(' ')[0].replace(".", ""))
                except:
                    review_score = ''
                    review_count = ''
            
            # Stok kontrolü.
            try:
                soup.select('#availability .a-color-state')[0].get_text().strip()
                stock = 'Out of Stock'
            except:
                try:
                    soup.select('#availability .a-color-price')[0].get_text().strip()
                    stock = 'Out of Stock'
                except:
                    stock = 'Available'

            log = pd.DataFrame({'date': now.replace('h',':').replace('m',''),
                                'code': prod_tracker.code[x], # excellde ki kod alanına koyduğunuz değer
                                'url': url,
                                'title': title,
                                'fiyat': prod_tracker.fiyat[x], # fiyat için koyulan değer
                                'price': price,
                                'stock': stock,
                                'review_score': review_score,
                                'review_count': review_count}, index=[x])

            try:
                # E-mail gönderim fonksiyonu
                if price < prod_tracker.fiyat[x]:
                    print('************************ UYARI! STOK VAR '+prod_tracker.code[x]+' ************************')
                    sender = 'contact@nemesispharma.com'
                    receivers = ['umut@umutemre.com']
                    msg = MIMEMultipart()
                    message = "Ps5 Stok Var : "+url+""
                    password = "umut4750787"
                    msg['From'] = "infinitumcomtr@gmail.com"
                    msg['To'] = "umut@umutemre.com"
                    msg['Subject'] = "PS5 Stok "+code+""

                    msg.attach(MIMEText(message, 'plain'))

                    server = smtplib.SMTP('smtp.gmail.com: 587')

                    server.starttls()

                    server.login(msg['From'], password)
                    server.sendmail(msg['From'], msg['To'], msg.as_string())
                    server.quit()
                    print("Gönderildi")
                    
            except:
                pass
                print("Hala Stok Yok...")
                gi
            tracker_log = tracker_log.append(log)
            print('Sorgulanan Ürün: '+ prod_tracker.code[x] +'\n' + title + '\n\n')            
            sleep(5)
        
       
    
    # arama geçmişinin kaydı
    last_search = glob('/arananlar/*.xlsx')[-1] # dosya konumu
    search_hist = pd.read_excel(last_search)
    final_df = search_hist.append(tracker_log, sort=False)
    
    final_df.to_excel('/arananlar/arama_gecmisi_{}.xlsx'.format(now), index=False)
    print('Arama sona erdi.')

search_product_list()
