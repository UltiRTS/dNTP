import os
import ipfshttpclient
from ipfshttpclient.multipart import FilesStream
from termcolor import colored


class DntpFileSystem:
    
    def __init__(self, addr:str='/dns/localhost/tcp/5001/http', mapDir:str='/maps') -> None:
        self._client = ipfshttpclient.Client(addr)
        self._mapDir = mapDir
        try: 
            # try to access dir stat
            self._client.files.ls(mapDir)
        except ipfshttpclient.exceptions.ErrorResponse as e:
            # if dir not exists then mkdir
            self._client.files.mkdir(mapDir)

        print(colored('[INFO]', 'green'), 'ifps client initialized.')

    def mkdirs(self, dirs:list):
        for directory in dirs:
            try:
                # prefix
                if not directory.startswith('/'): directory = '/' + directory
                self._client.files.mkdir(directory)
            except ipfshttpclient.exceptions.ErrorResponse as e:
                print(colored('[WARN]', 'yellow'), e, 'when make directory')


    def add2fs(self, realFileLoc:str, filename:str, storeDir=None):
        if not storeDir: storeDir = self._mapDir

        storeLoc = os.path.join(storeDir, filename)

        print(colored('[INFO]', 'cyan'), 'adding ', storeLoc, ' to ipfs.')

        try:
            self._client.files.write(path=storeLoc, file=realFileLoc, create=True)
            print(colored('[INFO]', 'green'), 'ipfs file loc: {0} add successful.'.format(storeLoc)) 
        except ipfshttpclient.exceptions.ErrorResponse as e:
            print(colored('[WARN]', 'yellow'), e)

        return self._client.files.stat(storeLoc)['Hash']
        

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
