from bs4 import BeautifulSoup
from flask import Flask
from flask import jsonify
import urllib3
import requests
from time import sleep
import random
import re
import csv
import json
import os

from datetime import datetime
import pickle
#  specification of the URL
#  KEEP A NOTE OF ALL THE HEAD URL BEING USED

from flask import request

app = Flask(__name__)

@app.route('/scrape', methods = ['POST'])

def scrapeIndeed():
    if request.method == 'POST':

        data = json.loads(request.data)
        print('data-------', data)
        if 'inputstring' not in data:
            return 'data is required'

        def make_head_url(in_str, new_parameter):
            first_split = in_str.split('&', 1)
            first_first_split = first_split[0].split('=', 1)[0]
            new_url = first_first_split + '=' + new_parameter + '&' + first_split[1]
            return new_url


        head_url = 'https://www.indeed.co.in/jobs?q=hr+executive&start='
        
        head_url = make_head_url(head_url, data['inputstring'].replace(' ', '+'))
        #print('head_url=====', head_url)
        # url = 'https://www.indeed.co.in/jobs?q=software%20engineer&ts=1547016759577&rq=1&fromage=last&vjk=694eb9cdd1efed89'
        # url = 'https://www.indeed.co.in/viewjob?jk=a534ccf89b38ce2a&tk=1d0pc1ha6148f000&from=serp&alid=3&advn=3689438429469462&sjdu=0ZFwD5rbjMRcHz87Kzx_g3VAf6vGaOujERp37xecDaesoMEMoNS2MJCRdYHyQUF2w7gQXmEBTTK9pKScnj0xHnrjKOPNpg7sMn_J-ME6cl8'


        def process_str(in_str):
            print(in_str)
            return in_str.split('&', 1)[-1]

        def cleanhtml(raw_html):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext

        JD = []    
        with open(os.getenv('BASE_ROOT_PATH') + '/Scrapper/scrapped_indeed.com/id_container.pkl', 'rb') as f:
            id_container = pickle.load(f)

            
        def save_jd(ID_list):
            print('id list===================', ID_list)
            url_sub = 'https://www.indeed.co.in/viewjob?jk=4a929d8bec02c3f7&from=serp&vjs=3'
            for i in ID_list:
            #     process url
                break_url_at_jk = url_sub.split('jk=')
                break_url_at_and = process_str(break_url_at_jk[1])
                new_url = break_url_at_jk[0] + 'jk=' + i[1] + '&' + break_url_at_and
                print(new_url)
            #      get the url content
                delay = random.random()
                sleep(float(delay))
                response = http.request('GET', new_url)
                soup = BeautifulSoup(response.data, "html.parser")

                containers = soup.find('div', {'class': 'jobsearch-JobComponent-description'})
            #     print(containers)
            #    get data on the webpage that is the actual JD
                page_content = ''
                for component in containers:
                    container = cleanhtml(str(component))
                    page_content = page_content + '\n' + container
                    print('----------------------------------------------------------------------------------')
                file_name = str(i[1]) + '.txt'
                f= open(os.getenv('BASE_ROOT_PATH') + '/Scrapper/scrapped_indeed.com/scrapped_jds/' + file_name, "w+", encoding="utf-8")
                f.write(page_content)
                f.close() 
                
                
                
        #  will capture the entire page
        for page_index in range(0,50,1):
            url = head_url + str(page_index)
            print(url)
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            http = urllib3.PoolManager()
            response = http.request('GET', url)            
            soup = BeautifulSoup(response.data, "html.parser")
            containers = soup.find_all('div', {'class': 'jobsearch-SerpJobCard unifiedRow row result'})
            #print('!!!!!!!!!!!!!!!!!!!!1', containers)
            ID_list = []
            for i in containers:
                temp_id = (i.get('id'))
                ID = temp_id.split('_')
                if ID[1] in id_container:
                    continue
                id_container[ID[1]] = 1
                ID_list.append(ID)
            print(len(ID_list))
            save_jd(ID_list)
            
            
            
        with open(os.getenv('BASE_ROOT_PATH') + '/Scrapper/scrapped_indeed.com/id_container.pkl', 'wb') as f:
            pickleData = pickle.dump(id_container, f)
            return jsonify(pickleData)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='4997')