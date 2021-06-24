import re
import requests
import threading
from bs4 import BeautifulSoup
from difflib import SequenceMatcher



class SpringCrapper(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(SpringCrapper)
		self.mapInfo = {}
		self.targetUrl = "https://api.springfiles.com/files/maps/"

	def run(self):
		try:
			resp = requests.get(self.targetUrl)
			soup = BeautifulSoup(resp.text, 'html.parser')
			allATags = soup.select('a')
			for tag in allATags:
				tagHref = tag['href']
				if tagHref.endswith('sd7') or tagHref.endswith('sdz'):
					self.mapInfo[tagHref]=['']
					self.mapInfo[tagHref][0]=self.targetUrl + tagHref
			print('[dNTP] sf sc finished')
		except Exception as e:
			print('[dNTP] spring sc lost contact with spring ')
		return 

if __name__ == '__main__':
    sc = SpringCrapper()
    sc.start()
    print(sc.mapInfo)
