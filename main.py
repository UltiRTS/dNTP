import os
import requests
import random
from threading import Thread

from six import with_metaclass
from termcolor import colored
from indexbuilder import buildIndex
from zkscrapper import ZeroKScrapper
from springCrapper import SpringCrapper
from dntpFilesystem import DntpFileSystem

failedDownloads={}
downloadedmap=0
maptotal=0

def downloader():
	global downloadedmap
	global failedDownloads
	global zk
	while zk.mapInfo:
		key=random.choice(list(zk.mapInfo.keys()))
		
		tmpUrls=zk.mapInfo[key].copy()
		del zk.mapInfo[key]    #do not let others access it once I start to work on it
		
		
		i=-1
		
		
		if doIhaveDis(key):
			downloadedmap+=1
			continue   #move on to the next if there is already one copy on disk
		
		while i<len(tmpUrls)-1:
			try:
				i+=1
				if tmpUrls[i]=='':
					continue
					
				resp = requests.get(tmpUrls[i],timeout=10)
				if resp.status_code != 200:
					if i==len(tmpUrls)-1:
						print('[dNTP] Error downloading map'+key+' from :'+str(tmpUrls)+' Http Code: '+resp.status_code+' Server Msg:'+ resp.content+' Retry: '+str(i)+'out of'+ str(len(tmpUrls)))
						failedDownloads[key]=tmpUrls.copy()
					
					continue   #try the next url in the list

				with open(os.path.join('tmpMap', key), 'wb') as f:
					f.write(resp.content)
					downloadedmap+=1
					print("[dNTP] Downloaded map "+key+' '+str(downloadedmap)+'/ '+str(maptotal))
					break
			
			except Exception as e:
				failedDownloads[key]=tmpUrls.copy()
				print('[dNTP] Error downloading map:'+ key+' urls:'+ str(tmpUrls)+'local Exception:'+ str(e)+' Retry: '+str(i)+'out of'+ str(len(tmpUrls)))

			
				

def doIhaveDis(targetFile):
	for filename in os.listdir('finalMap/'):
		if targetFile == filename:
			return True
	for filename in os.listdir('tmpMap/'):
		if targetFile == filename:
			return True
	#for filename in os.listdir('maps/redacted'):
		#if targetFile == filename:
			#return True


if __name__ == '__main__':
	#os.system('rm -rf maps/')
	#if not os.path.exists('maps'):
		#os.mkdir('maps')
	#if not os.path.exists('redacted'):
		#os.mkdir('redacted')
    
	zk = ZeroKScrapper()
	sc = SpringCrapper()
	zk.start()
	print('[dNTP] zk sc started')
	sc.start()
	print('[dNTP] sf sc started')
	print('[dNTP] still waiting for worker process to exit')
	zk.join()
	sc.join()
	for key in sc.mapInfo:
		try:
			zk.mapInfo[key][0]=sc.mapInfo[key][0]   #use springscrappers links to replace links in the zk indexer
		except:
			zk.mapInfo[key]=['']
			zk.mapInfo[key][0]=sc.mapInfo[key][0]  #if the entry does not exist, create a new entry and do the above again
			
	print('[dNTP] downloading')
	
	maptotal=len(zk.mapInfo)
	#downloader(zk.mapInfo)
	
	threads = []
	
	t = Thread(target=downloader, args=())
	t.start()
	threads.append(t)

	t = Thread(target=downloader, args=())
	t.start()
	threads.append(t)

	t = Thread(target=downloader, args=())
	t.start()
	threads.append(t)

	t = Thread(target=downloader, args=())
	t.start()
	threads.append(t)
	
	t = Thread(target=downloader, args=())
	t.start()
	threads.append(t)

	t = Thread(target=downloader, args=())
	t.start()
	threads.append(t)

	for j in threads:
		j.join()
	print("[dNTP] Failed downloads: "+str(failedDownloads))	

	buildIndex()


	DFS = DntpFileSystem()
	DFS.putIntoIPFS()

