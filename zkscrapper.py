import os
import requests
from bs4 import BeautifulSoup

# offset start at 40 end at 200
class ZeroKScrapper:

	def __init__(self, defaultDetailFilePath=None):
		self.targetUrl = "http://zero-k.info/Maps"
		self.base = "http://zero-k.info"
		self.defaultInfoPath = 'mapInfo.csv'
		self.session = requests.session()
		self.formData = {
            "mapSupportLevel": 2,
            "size": "any",
            "sea": "any",
            "hills": "any",
            "elongated": "any",
            "assymetrical": "any",
            "special": 0,
            "isTeams": "Any",
            "is1v1": "any",
            "ffa": "any",
            "chicken": "any",
            "isDownloadable": 1,
            "needsTagging": "false",
            "search": "",
            "offset": 40
        }
		if defaultDetailFilePath:
			self.mode = "UPDATE"
		else:
			self.mode = "INIT"
			if not os.path.exists(self.defaultInfoPath):
				try:
					os.mknod(self.defaultInfoPath)
				except:
					pass

		self.detailFilePath = defaultDetailFilePath
		# with map name and map download url
		self.mapInfo = []

	def _extractMapInfoFromDetailUrl(self, detailLink):
		resp = self.session.get(self.base + detailLink)
		soup = BeautifulSoup(resp.text, "html.parser")
		tags = soup.select('a')
		for tag in tags:
			if tag.get('href') and tag['href'].endswith('sd7'):
				found = {
					"mapName": os.path.basename(tag['href']),
					"url": tag['href']
				}
				return found

		return None

	def _getAllMapInfo(self):
		if self.mode == "INIT":
			# first operation is get,
			# then all the operation is post 
			resp = self.session.get(self.targetUrl)
			soup = BeautifulSoup(resp.text, "html.parser")
			detailLinks = []
			tags = soup.select('a')
			for tag in tags:
				if tag.get('href') and tag['href'].startswith("/Map"):
					detailLinks.append(tag['href'])

			for offset in range(40, 201, 40):
				self.formData['offset'] = offset
				resp = self.session.post(
					self.targetUrl, 
					json=self.formData
				)
				soup = BeautifulSoup(resp.text, "html.parser")
				links = [tag['href'] for tag in soup.select('a')]
				detailLinks.extend(links)

			for detailLink in detailLinks:
				info = self._extractMapInfoFromDetailUrl(detailLink)
				if info:
					self.mapInfo.append(info)
					with open(self.defaultInfoPath, 'a') as f:
						f.write("{0},{1}".format(info['mapName'], info['url']))
						print("Wrote map -> {0}, url -> {1}".format(info['mapName'], info['url']))
		else:
			with open(self.detailFilePath, "r") as f:
				mapInfoLines = f.readlines()
				for line in mapInfoLines:
					mapName, url = line.split(',')
					self.mapInfo.append({
						"mapName": mapName,
						"url": url
					})
				
				



				

if __name__ == '__main__':
	zk = ZeroKScrapper()
	zk._getAllMapInfo()
	print(zk.mapInfo)