import os
import ipfsApi
import time
from threading import Thread
api = ipfsApi.Client('127.0.0.1', 5001)

def startIPFS():
	os.system("ipfs daemon")

def addFiles():
	ret={}
	#infoArray=api.add('maps', recursive=True)
	for filename in os.listdir('maps/'):
		#print (api.add('maps/'+filename))
		ret[filename]=api.add('maps/'+filename)[0]['Hash']
	
	return ret
		

if __name__ == '__main__':
	ipfs = Thread(target=startIPFS, args=())
	ipfs.start()
	time.sleep(20)
	print(str(addFiles()))
	#addFiles()
	
#j.join()
		


















