import re
import requests
import threading
from bs4 import BeautifulSoup
from difflib import SequenceMatcher



class SpringCrapper(threading.Thread):

    def __init__(self, ratio=0.7, retry=3):
        threading.Thread.__init__(SpringCrapper)
        self.urls = []
        self.targetUrl = "https://api.springfiles.com/files/maps/"
        self.compareRatio = ratio
        self.retry = 3

    def _extractAllMapUrls(self):
        resp = requests.get(self.targetUrl)
        soup = BeautifulSoup(resp.text, 'html.parser')
        allATags = soup.select('a')
        for tag in allATags:
            tagHref = tag['href']
            if tagHref.endswith('sd7') or tagHref.endswith('sdz'):
                self.urls.append(tagHref)
        
        return len(self.urls)
    
    def _getAllLatestMap(self):
        index = 0
        urlLenth = len(self.urls)
        while index+1 < urlLenth:
            curMapName = self.urls[index].split('_')[0]
            nextMapName = self.urls[index+1].split('_')[0]
            # if next map name is very similiar to current one delete current one
            # cuz the origin map list is ordered by version, SO the logic here is just fine
            if SequenceMatcher(None, curMapName, nextMapName).ratio() > self.compareRatio:
                self.urls.pop(index)
                urlLenth -= 1
            else: 
                index += 1
        
        #print(self.urls)
        return len(self.urls)

    def run(self):
        total = self._extractAllMapUrls()
        filtered = self._getAllLatestMap()
        print("Total map is {0}, aftering filter we have {1}".format(total, filtered))
        urlLen = len(self.urls)
        i = 0
        while i < urlLen:
            try:
                resp = requests.get(self.targetUrl + self.urls[i])
                with open('maps/' + self.urls[i], 'wb') as f:
                    f.write(resp.content)
                
                print("downloaded {0}".format(self.urls[i]))
                i += 1
            except Exception as e:
                if self.retry < 0:
                    # reset retry
                    self.retry = 3
                    i += 1
                print("{0} failed as error {1}".format(self.urls[i], e))
                self.retry -= 1
                print("retrying left {0}".format(self.retry))