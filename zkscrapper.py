import os
import requests
import threading
from bs4 import BeautifulSoup

# offset start at 40 end at 200
class ZeroKScrapper(threading.Thread):

	def __init__(self, defaultDetailFilePath=None):
		threading.Thread.__init__(ZeroKScrapper)
		self.targetUrl = "http://zero-k.info/Maps"
		self.base = "http://zero-k.info"
		self.defaultInfoPath = 'mapInfo.csv'
		self.session = requests.session()
		self.formData = {
            "mapSupportLevel": 'Any',
            "size": "any",
            "sea": "any",
            "hills": "any",
            "elongated": "any",
            "assymetrical": "any",
            "special": -1,
            "isTeams": "Any",
            "is1v1": "any",
            "ffa": "any",
            "chicken": "any",
            "isDownloadable": 1,
            "needsTagging": "false",
            "search": "",
            "offset": 40
        }

		self.detailFilePath = defaultDetailFilePath
		# with map name and map download url
		self.mapInfo = {}

	def _extractMapInfoFromDetailUrl(self, detailLink):
		found={}
		
		resp = self.session.get(self.base + detailLink)
		soup = BeautifulSoup(resp.text, "html.parser")
		tags = soup.select('a')
		for tag in tags:
			if tag.get('href') and tag['href'].endswith('sd7'):
				found[os.path.basename(tag['href'])]=['']
				
				found[os.path.basename(tag['href'])].append(tag['href'])
				
		return found

		

	def Merge(self,dict1, dict2):
    		return(dict2.update(dict1))

	def run(self):
		resp = self.session.get(self.targetUrl)
		soup = BeautifulSoup(resp.text, "html.parser")
		detailLinks = []
		tags = soup.select('a')
		for tag in tags:
			if tag.get('href') and tag['href'].startswith("/Map"):
				detailLinks.append(tag['href'])
				
		
		pageCount = 0
		offset = 40
		while True:
			self.formData['offset'] = offset
			resp = self.session.post(
				self.targetUrl, 
				json=self.formData
			)
			
			soup = BeautifulSoup(resp.text, "html.parser")
			links = [tag['href'] for tag in soup.select('a')]
			print(links)

			if links == []:
				break

			pageCount += 1
			detailLinks.extend(links)

			offset += 40

		for detailLink in detailLinks:
			info = self._extractMapInfoFromDetailUrl(detailLink)
			if info:
				self.Merge(info,self.mapInfo)
		print('[dNTP] zk sc finished')

		print(pageCount)
		return

				



				

if __name__ == '__main__':
	zk = ZeroKScrapper()
	zk.start()
	zk.join()
