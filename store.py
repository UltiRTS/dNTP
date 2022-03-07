import os
import re
import queue
import shutil
import sqlite3
import hashlib
import json

from termcolor import colored
from lib.unitSync import UnitSync





class fileStorager():
	def __init__(self,startDir= os.getcwd()):
		
		self.startDir=startDir
		self.DB_CONF = {'DB_name': self.startDir+'/info.db','schema_loc': 'schema.sql'}

	def initDB(self):
		database_name=self.DB_CONF['DB_name']
		schema_loc=self.startDir+'/'+self.DB_CONF['schema_loc']
		conn = sqlite3.connect(database_name)
		cur = conn.cursor()

		with open(schema_loc, 'r') as fp:
			cur.executescript(fp.read())
			conn.commit()
		
		print(colored('[INFO]', 'green'), 'Initialized db')



		
	def updateMaps(self,tmp='tmpMap', engineLoc='engine'):
		err = None
		if not os.path.exists(tmp):
			print(colored('[ERRO]', 'red'), tmp, "not exists.")
			err = 'dir not exists'
		if not os.path.exists(engineLoc):
			print(colored('[ERRO]', 'red'), engineLoc, "not exists.")
			err = 'dir not exists'

		if err:
			return 
		

		libPath = os.path.join(self.startDir, engineLoc, 'libunitsync.so')
		
		uSync = UnitSync(self.startDir, libPath)


		tempMaps = os.listdir(tmp)
		#ngineMapDirLoc = os.path.join(engineLoc, 'maps')
		#failed= True
		conn = sqlite3.connect(self.DB_CONF['DB_name'])
		cur = conn.cursor()

		# tempMap is file name of map
		for tempMap in tempMaps:
			if not tempMap.endswith('.png'):	
				# move current map file to `engine/maps`
				shutil.copy(self.startDir+'/tmpMap/'+tempMap, self.startDir+'/engine/maps/')
				# reinit unitsync everytime
				uSync.reinit()
				try:
					mapName = uSync.getMapName()
					minimapPath=uSync.storeMinimap(mapName)
					print(colored('[INFO]', 'green'), "Generated info for map "+str(os.listdir(self.startDir+'/engine/maps/'))+' minimap stored in '+ minimapPath, end = "\r")

				except Exception as e:
					print(e)
					print(colored('[ERRO]', 'red'), "Invalid Map (it's now deleted)"+str(os.listdir(self.startDir+'/engine/maps/'))+' named '+mapName.ljust(150))
					os.system('rm '+self.startDir+'/engine/maps/*')
					os.system('rm '+self.startDir+'/tmpMap/'+tempMap)
					continue
					
				
				minimapFilename = minimapPath.split('/')[-1]
				
				mapHash = self._hashFile(self.startDir+'/tmpMap/'+tempMap)
				os.system('rm '+self.startDir+'/engine/maps/*')
				# check if map already exists in db, if yes, do nothing, if no, insert record
				cur.execute("SELECT * FROM maps WHERE map_hash = ?", (mapHash,))
				if cur.fetchone():
					print(colored('[INFO]', 'green'), "Map already exists in db, skipping...")
					continue
				else:
					cur.execute("INSERT INTO maps (map_name, map_filename, minimap_filename, map_hash) VALUES (?, ?, ?, ?)", (mapName, tempMap, minimapFilename, mapHash))
					#conn.commit()
					print(colored('[INFO]', 'green'), "Added map to db: "+mapName)
					

				
                                # after finishing, move file to `finalMap/`

				conn.commit()



	def updateArchive(self,archiveDir='/opt/archives'):
		with open("/opt/archives/path.json") as json_file:
			pathData = json.load(json_file)

			conn = sqlite3.connect(self.DB_CONF['DB_name'])
			cur = conn.cursor()

			archives = os.listdir(archiveDir)
			print(colored('[INFO]', 'green'), 'archives in monitoring dir '+archiveDir+': '+str(archives))
			
			failed= True
			while failed:
				try:
					self.initDB()
					conn = sqlite3.connect(self.DB_CONF['DB_name'])
					cur = conn.cursor()
					cur.execute('DELETE FROM archives')
					conn.commit()
					failed=False
				except:
					failed=True
					print('failed to update db')
			
			for archive in archives:
				if archive.endswith('.json'):
					print(colored('[INFO]', 'green'), 'skipping json'+archive)
					continue
						

				try:
					archiveHash = self._hashFile(archiveDir+'/'+archive)
					print(colored('[INFO]', 'green'), 'got hash for archives'+archive)
				except:
					continue
				try:
					cur.execute('INSERT INTO archives \
					(zip_name, extract_to, zip_hash) \
					values \
					(?, ?, ?)', 
					(archive, pathData[archive], archiveHash))
					print(colored('[INFO]', 'green'), 'write hashdb for archives'+archive)
				except:
					print('undocumented files '+ archive)
				
				conn.commit()


	def _hashFile(self,file_path):
		"""_hashFile.
		fed with file_path return 32 chars md5 hash

		:param file_path:
		"""
		
		with open(file_path, 'rb') as f:
			toHash = f.read()

		return hashlib.md5(toHash).hexdigest()
				




if __name__ == '__main__':
	pass
