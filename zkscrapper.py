from urllib import request
import random
import _thread
import threading
import urllib.request
import os
from bs4 import BeautifulSoup




class zkScrap(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.urls=[]
		i=0
		while i<10000:
			self.urls.append(i)   #download list generation
			i+=1
	
	def run(self):
		while True:
			urlNum=random.choice(self.urls)   #randomly downloads from the list
			
			response = request.urlopen("http://zero-k.info/Maps/Detail/"+str(urlNum))
			# set the correct charset below
			page_source = response.read().decode('utf-8')
			if not 'WARNING, THIS MAP IS NOT AND WILL NOT BE DOWNLOADABLE.' in page_source:
				soup = BeautifulSoup(page_source)
				x=soup.findAll('a')
				for i in x:
					try:
						if '.sd7' in i['href']:
							print(i['href'])
							url = i['href']
							try:
								urllib.request.urlretrieve(url, 'maps/'+os.path.basename(url))  #go to the next list downloads
								self.urls.remove(urlNum)#put back if all downloads fail
								break
							except:
								continue   #go to the second mirror if the first one fails
					except:
						print("page does not contain a href:"+str(i))
					
					
					
				
				#x=soup.findAll('img')
				#for i in x:
					#if 'minimap.jpg' in i['src']:
						#print(i['src'])
						#url = i['src']
						#try:
							#urllib.request.urlretrieve(url, '/maps/'+os.path.basename(url))
						#except:
							#print('unable to get minimap for '+url)
							
								#x=soup.findAll('a')
				#x=soup.findAll('img')
				#for i in x:
					#if 'heightmap.jpg' in i['src']:
						#print(i['src'])
						#url = i['src']
						#try:
							#urllib.request.urlretrieve(url, '/maps/'+os.path.basename(url))
						#except:
							#print('unable to get minimap for '+url)
							
								#x=soup.findAll('a')