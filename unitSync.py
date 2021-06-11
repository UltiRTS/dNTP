import numpy as np
from PIL import Image
from bitstring import BitArray, ConstBitStream
import ctypes
from multiprocessing.pool import ThreadPool
import os
from difflib import SequenceMatcher
from numpy.lib.type_check import _imag_dispatcher

from termcolor import colored


class UnitSync:
	def __init__(self, startdir,libunitsync_path,username='unknown'):
		self.so = ctypes.CDLL(libunitsync_path)
		self.init = self.so.Init(0, 0)
		self.write_dir = self.so.GetWritableDataDirectory()
		self.username=username
		self.startdir=startdir
		os.chdir(self.startdir)
		# Some Dynamic functions
		self._getMapCount = self.so.GetMapCount
		self._getMapName = self.so.GetMapName
		self._getMapFileName = self.so.GetMapFileName
		self._getMapArchiveName = self.so.GetMapArchiveName
		self._getMinimap = self.so.GetMinimap
		# output settings
		self._getMapCount.restype = ctypes.c_int
		self._getMapName.restype = ctypes.c_char_p
		self._getMapFileName.restype = ctypes.c_char_p
		self._getMapArchiveName.restype = ctypes.c_char_p

		self.mapNames = []

    def reinit(self):
        self.init = self.so.Init(0, 0)
	
	def _similiar(self, a, b):
		return SequenceMatcher(None, a, b).ratio()

	def mapList(self):
		mapList = []
		mapCount = self._getMapCount()
		for i in range(mapCount):
			mapList.append(self._getMapName(i).decode('utf8'))
		os.chdir(self.startdir)

		self.mapNames = mapList

		return mapList

	def _getImg(self, mapname, reduction=0):
		width = height = 1024 // 2**reduction
		self._getMinimap.restype = ctypes.POINTER(ctypes.c_ubyte * (width * height * 2))
		minimapData = self._getMinimap(mapname.encode('utf8'), reduction).contents
#		have, need = len(minimapData), width*height*2
#		print(have, need)
#		if have < need:
#			print("No much data fixing.")
#			emptyFix = bytes(need-have)
#			minimapData += emptyFix

		mapname.replace(' ', '_')
		img = Image.frombytes('RGB', (width, height), minimapData, 'raw', 'BGR;16' )

		return img

	def storeMinimap(self, mapname, storage="finalMap"):
		minimapStorePath = os.path.join(storage, mapname.replace(' ', '🦔') + '.png')
		for reduction in range(0,9):
			try:
				img = self._getImg(mapname, reduction)
				break
			except:
				#print(colored("ERROR", 'red'), "No much data reduce width and height.")
				pass
		img.save(minimapStorePath)


		return minimapStorePath
		
		
	def getMapName(self):
		self._getMapCount()
		return self._getMapName(0).decode('utf8')



if __name__ == '__main__':
	cur = os.getcwd()
	
	us = UnitSync(cur,cur + '/engine/libunitsync.so')
	print(us._getMapCount())
	us.mapList()
	print(us.mapNames[2])
	us.storeMinimap(us.mapNames[2])
