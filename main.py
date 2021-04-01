import os
import requests
import threading
from zkscrapper import zkScrap
from springCrapper import SpringCrapper
from difflib import SequenceMatcher


class Downloader(threading.Thread):
    '''
    To plugin another downloader for map filter
    the other downloader/mapListGetter must have these attr
    - mapNames
    - targetUrl
    - _extractAllMapNames
    '''

    def __init__(self, downloaders=[], ratio=0.7, retry=3):
        threading.Thread.__init__(Downloader)

        self.downloaders = downloaders
        self.targets = []
        self.mapNames = []
        self.compareRatio = ratio
        self.retry = retry
        self.defaultRetry = retry
    
    def _getAllLatestMap(self):
        # sort all mapNames first
        self.mapNames.sort(key=lambda x: x.get('mapName'))

        mapNameIndex = 0
        mapNamesLen = len(self.mapNames)

        while mapNameIndex+1 < mapNamesLen:
            curMapName = self.mapNames[mapNameIndex]['mapName']
            nextMapName = self.mapNames[mapNameIndex+1]['mapName']

            if SequenceMatcher(None, curMapName, nextMapName).ratio() > self.compareRatio:
                self.mapNames.pop(mapNameIndex)
                mapNamesLen -= 1
            else:
                mapNameIndex += 1
            
        return mapNamesLen

    def run(self):
        targetId = 0
        for downloder in self.downloaders:
            print("Parsing target url: ", downloder.targetUrl)
            downloder._extractAllMapNames()
            self.targets.append(downloder.targetUrl)
            for mapName in downloder.mapNames:
                self.mapNames.append({
                    "targetUrlId": targetId,
                    "mapName": mapName
                })
            
            targetId += 1

        print("Parsing finished. All map count: ", len(self.mapNames))

        # vague filter
        mapCount = self._getAllLatestMap()
        print("Got all latest maps. map count: ", mapCount)

        # start downloading 
        mapIndex = 0
        while mapIndex < mapCount:
            mapName = self.mapNames[mapIndex]
            try:
                url = self.targets[mapName['targetUrlId']] + mapName['mapName']
                resp = requests.get(url)
                with open('maps/' + mapName['mapName'], 'wb') as f:
                    f.write(resp.content)
                
                print("Downloaded {0}".format(mapName['mapName']))
                mapIndex += 1
            except Exception as e:
                if self.retry < 0:
                    self.retry = self.defaultRetry
                    mapIndex += 1 
                else: 
                    print("Download failed {0} retrying {1} times".format(e, self.retry))
                    self.retry -= 1


if __name__ == '__main__':

    if not os.path.exists('maps'):
        os.makedirs('maps')

    zk=zkScrap()
    sc = SpringCrapper()

    dl = Downloader(downloaders=[sc,])
    dl.start()