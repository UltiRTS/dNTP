import os
import ipfshttpclient
from ipfshttpclient.multipart import FilesStream
from six import create_bound_method
from termcolor import colored


class DntpFileSystem:
    
    def __init__(self, addr:str='/dns/localhost/tcp/5001/http', mapDir:str='/maps') -> None:
        self._client = ipfshttpclient.Client(addr)
        self._mapDir = mapDir
        try:
            self._client.files.mkdir(mapDir)
        except ipfshttpclient.exceptions.ErrorResponse as e:
            print(colored('[WARN]', 'yellow'), ' ', e)

        print(colored('[INFO]', 'green'), ' ifps client initialized.')

    def add2fs(self, realFileLoc:str, filename:str, storeDir=None):
        if not storeDir: storeDir = self._mapDir

        storeLoc = os.path.join(storeDir, filename)

        try:
            self._client.files.write(path=storeLoc, file=realFileLoc, create=True)
            print(colored('[INFO]', 'green'), ' ipfs file loc: {0} add successful.'.format(storeLoc)) 
        except ipfshttpclient.exceptions.ErrorResponse as e:
            print(colored('[WARN]', 'yellow'), ' ', e)
        

    def retriveMapsMap(self, storeDir=None):
        if not storeDir: storeDir = self._mapDir

        entry = self._client.files.ls(storeDir)['Entries']

        resMap = {}
        for e in entry:
            filename = e['Name']
            ipfsHash = self._client.files.stat(os.path.join(storeDir, filename))['Hash']

            resMap[filename] = ipfsHash
        
        return resMap

    def putIntoIPFS(self):
		
		arr = os.listdir('finalMap/')
		for filename in arr:
			if not filename.endswith('png'):
				self.add2fs('finalMap/' + filename, filename.split('.')[0])	

		ipfsInfo = self.retriveMapsMap()

		with open('finalMap/ipfs.txt', 'w') as f:
			for info in ipfsInfo.items():
				f.write(info[0] + ',' + info[1] + '\n')
		print(colored('[INFO]', 'green'), 'ipfs info wrote at', 'finalMap/ipfs.txt')
		
if __name__ == '__main__':
    DFS = DntpFileSystem()
    # testfile must exists
    DFS.add2fs('testfile', 'testfile')
    hashMap = DFS.retriveMapsMap()
    print(hashMap)
