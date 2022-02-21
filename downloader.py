

import os
import requests
import random
import store
import time
from threading import Thread

from termcolor import colored
from lib.zkscrapper import ZeroKScrapper
from lib.springCrapper import SpringCrapper



class mapDownloader():
	def __init__(self):
		self.failedDownloads={}
		self.downloadedmap=0
		self.maptotal=0
		self.zk = ZeroKScrapper()
		self.sc = SpringCrapper()
		
	def downloader(self):
		self.downloadedmap
		self.failedDownloads
		
		while self.zk.mapInfo:
			key=random.choice(list(self.zk.mapInfo.keys()))
			
			tmpUrls=self.zk.mapInfo[key].copy()
			del self.zk.mapInfo[key]    #do not let others access it once I start to work on it
			
			
			i=-1
			
			
			if self.doIhaveDis(key):
				self.downloadedmap+=1
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
							self.failedDownloads[key]=tmpUrls.copy()
						
						continue   #try the next url in the list

					with open(os.path.join('tmpMap', key), 'wb') as f:
						f.write(resp.content)
						self.downloadedmap+=1
						print(("[dNTP] Downloaded map "+key+' ').ljust(150)+str(self.downloadedmap)+'/ '+str(self.maptotal), end = "\r")
						break
				
				except Exception as e:
					self.failedDownloads[key]=tmpUrls.copy()
					print('[dNTP] Error downloading map:'+ key+' urls:'+ str(tmpUrls)+'local Exception:'+ str(e)+' Retry: '+str(i)+'out of'+ str(len(tmpUrls)))

				
					

	def doIhaveDis(self,targetFile):

		for filename in os.listdir('tmpMap/'):
			if targetFile == filename:
				return True

	def download(self):
		
		try:
			self.zk.start()
			print('[dNTP] zk sc started')
		except Exception as e:
			print('[dNTP] zk sc lost contact with zk '+e)
		
		
		
		self.sc.start()
		print('[dNTP] sf sc started')
		
		
		
		print('[dNTP] still waiting for worker process to exit')
		self.zk.join()
		self.sc.join()
		for key in self.sc.mapInfo:
			try:
				self.zk.mapInfo[key][0]=self.sc.mapInfo[key][0]   #use springscrappers links to replace links in the zk indexer
			except:
				self.zk.mapInfo[key]=['']
				self.zk.mapInfo[key][0]=self.sc.mapInfo[key][0]  #if the entry does not exist, create a new entry and do the above again
				
		print('[dNTP] downloading')
		
		self.maptotal=len(self.zk.mapInfo)
		#downloader(zk.mapInfo)
		
		threads = []
		
		t = Thread(target=self.downloader, args=())
		t.start()
		threads.append(t)
		t = Thread(target=self.downloader, args=())
		t.start()
		threads.append(t)
		t = Thread(target=self.downloader, args=())
		t.start()
		threads.append(t)
		t = Thread(target=self.downloader, args=())
		t.start()
		threads.append(t)
		
		t = Thread(target=self.downloader, args=())
		t.start()
		threads.append(t)
		t = Thread(target=self.downloader, args=())
		t.start()
		threads.append(t)
		for j in threads:
			j.join()
		print("[dNTP] Failed downloads: "+str(self.failedDownloads))	
