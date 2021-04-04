import os
import requests
import threading
from zkscrapper import ZeroKScrapper
from springCrapper import SpringCrapper
from difflib import SequenceMatcher


class Downloader(threading.Thread):
    '''
    To plugin another downloader for map filter
    the other downloader/mapListGetter must have these attr
    mapInfo -> [
        {
            "mapName": "",
            "url": ""
        }
    ]
    '''

    def __init__(self, scrappers = [], retry=3, ratio=0.7):
        threading.Thread.__init__(Downloader)

        self.compareRatio = ratio
        self.defaultRetry = retry

        self.mapInfo = []

        for scrapper in scrappers:
            scrapper._getAllMapInfo()
            self.mapInfo.extend(scrapper.mapInfo)
        
        print("Initialized.")
    
    def vagueFilter(self):
        self.mapInfo.sort(key=lambda x: x.get('mapName'))

        mapInfoIndex = 0
        infoCount = len(self.mapInfo)

        while mapInfoIndex+1 < infoCount:
            cur = self.mapInfo[mapInfoIndex]['mapName']
            next = self.mapInfo[mapInfoIndex+1]['mapName']

            if SequenceMatcher(None, cur, next).ratio() > self.compareRatio:
                self.mapInfo.pop(mapInfoIndex)
                infoCount -= 1 
            else:
                mapInfoIndex += 1
    
    def run(self):
        self.vagueFilter()
        index = 0
        retry = 3
        while index < len(self.mapInfo):
            mapInfo = self.mapInfo[index]
            try:
                resp = requests.get(mapInfo['url'])
                if resp.status_code != 200:
                    continue

                with open(os.path.join('maps', mapInfo['mapName']), 'wb') as f:
                    f.write(resp.content)
                    print("Downloaded {0}".format(mapInfo['mapName']))
                index += 1
            except Exception as e:
                if retry < 0:
                    retry = 3
                    index += 1
                print("error -> {0}, retrying {1} times.".format(e, retry))
                retry -= 1

    

if __name__ == '__main__':
    if os.path.exists('maps'):
        os.mkdir('maps')

    zk = ZeroKScrapper()
    sc = SpringCrapper()
    dl = Downloader(scrappers=[zk, sc])

    print("start downloading.")
    dl.start()