import re
import requests
import threading
from bs4 import BeautifulSoup
from difflib import SequenceMatcher



class SpringCrapper:

    def __init__(self):
        self.mapInfo = []
        self.targetUrl = "https://api.springfiles.com/files/maps/"

    def _getAllMapInfo(self):
        resp = requests.get(self.targetUrl)
        soup = BeautifulSoup(resp.text, 'html.parser')
        allATags = soup.select('a')
        for tag in allATags:
            tagHref = tag['href']
            if tagHref.endswith('sd7') or tagHref.endswith('sdz'):
                self.mapInfo.append({
                    "mapName": tagHref,
                    "url": self.targetUrl + tagHref
                })
        
        return len(self.mapInfo)

if __name__ == '__main__':
    sc = SpringCrapper()
    sc._getAllMapInfo()
    print(sc.mapInfo)