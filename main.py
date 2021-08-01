from store import fileStorager
from storageMonitor import OnMyWatch
from downloader import mapDownloader
from ipfsServer import ipfs
import os
import time 
if __name__ == '__main__':
	startDir = os.getcwd()
	ipfs().start()
	
	store=fileStorager(startDir)
	#os.system('rm -rf info.db')
	store.initDB()
	OnMyWatch().start()   #start monitoring archive changes
	
	
	download=mapDownloader()
	
	#store.initDB()
	
	while True:
		download.download()
		
		store.updateArchive()
		store.updateMaps()
		
		time.sleep(604800)
		#os.system('rm -rf info.db')

