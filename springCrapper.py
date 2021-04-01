import re
import requests
import threading
from bs4 import BeautifulSoup
from difflib import SequenceMatcher



class SpringCrapper(threading.Thread):

    def __init__(self, ratio=0.7, retry=3):
        threading.Thread.__init__(SpringCrapper)
        self.mapNames = []
        self.targetUrl = "https://api.springfiles.com/files/maps/"
        self.compareRatio = ratio
        self.retry = 3

    def _extractAllMapNames(self):
        resp = requests.get(self.targetUrl)
        soup = BeautifulSoup(resp.text, 'html.parser')
        allATags = soup.select('a')
        for tag in allATags:
            tagHref = tag['href']
            if tagHref.endswith('sd7') or tagHref.endswith('sdz'):
                self.mapNames.append(tagHref)
        
        return len(self.mapNames)
    
    def _getAllLatestMap(self):
        index = 0
        urlLenth = len(self.mapNames)
        while index+1 < urlLenth:
            curMapName = self.mapNames[index].split('_')[0]
            nextMapName = self.mapNames[index+1].split('_')[0]
            # if next map name is very similiar to current one delete current one
            # cuz the origin map list is ordered by version, SO the logic here is just fine
            if SequenceMatcher(None, curMapName, nextMapName).ratio() > self.compareRatio:
                self.mapNames.pop(index)
                urlLenth -= 1
            else: 
                index += 1
        
        #print(self.mapNames)
        return len(self.mapNames)

    def run(self):
        total = self._extractAllMapNames()
        filtered = self._getAllLatestMap()
        print("Total map is {0}, aftering filter we have {1}".format(total, filtered))
        urlLen = len(self.mapNames)
        i = 0
        while i < urlLen:
            try:
                resp = requests.get(self.targetUrl + self.mapNames[i])
                with open('maps/' + self.mapNames[i], 'wb') as f:
                    f.write(resp.content)
                
                print("downloaded {0}".format(self.mapNames[i]))
                i += 1
            except Exception as e:
                if self.retry < 0:
                    # reset retry
                    self.retry = 3
                    i += 1
                print("{0} failed as error {1}".format(self.mapNames[i], e))
                self.retry -= 1
                print("retrying left {0}".format(self.retry))