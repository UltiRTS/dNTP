import os
import re
import queue
import shutil
import sqlite3
import hashlib
import json

from termcolor import colored
from lib.dntpFilesystem import DntpFileSystem
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

	#this needs a revisit before actually putting into use
	def updateEngine(self,engine_loc='engine'):

		DFS = DntpFileSystem(mapDir='/engine')
		filelist = self.getFilelist(engine_loc)
		dirlist = self.getDirList(engine_loc)

		DFS.mkdirs(dirlist)

		conn = sqlite3.connect(self.DB_CONF['DB_name'])
		cur = conn.cursor()

		for i in range(len(filelist)):
			fileInfo = filelist[i]

			ipfs_store_loc = '/' + fileInfo['path'].split(fileInfo['filename'])[0]
			ipfs_addr = DFS.add2fs(fileInfo['path'], fileInfo['filename'], ipfs_store_loc)

			filelist[i]['ipfs_addr'] = ipfs_addr
			filelist[i]['md5'] = self._hashFile(fileInfo['path'])

			record = cur.execute('SELECT COUNT(*) from files where filename=? and extract_to=?', (fileInfo['filename'], ipfs_store_loc.lstrip('/'), ) ).fetchone()

			# if not exists then insert
			if record[0] == 0:
				cur.execute(
					'INSERT INTO files (filename, file_hash, extract_to, ipfs_addr) values (?,?,?,?)', 
					(filelist[i]['filename'], filelist[i]['md5'], ipfs_store_loc.lstrip('/'), ipfs_addr )
				) 
			else:
				cur.execute(
					'UPDATE files SET filename=?, file_hash=?, extract_to=?, ipfs_addr=? WHERE filename=? and extract_to=?', 
					(fileInfo['filename'], filelist[i]['md5'], ipfs_store_loc.lstrip('/'), ipfs_addr, fileInfo['filename'], ipfs_store_loc.lstrip('/'),) 
				)


		conn.commit()
		print(colored('[INFO]', 'green'), ' engine status updated.')




		
	def updateMaps(self,tmp='tmpMap', target='finalMap', engineLoc='engine'):
		err = None
		if not os.path.exists(tmp):
			print(colored('[ERRO]', 'red'), tmp, "not exists.")
			err = 'dir not exists'
		#if not os.path.exists(target):
			#print(colored('[ERRO]', 'red'), target, "not exists.")
			#err = 'dir not exists'
		if not os.path.exists(engineLoc):
			print(colored('[ERRO]', 'red'), engineLoc, "not exists.")
			err = 'dir not exists'

		if err:
			return 

		

		DFS = DntpFileSystem(mapDir='/maps')

		

		libPath = os.path.join(self.startDir, engineLoc, 'libunitsync.so')
		
		uSync = UnitSync(self.startDir, libPath)


		tempMaps = os.listdir(tmp)
		engineMapDirLoc = os.path.join(engineLoc, 'maps')
		failed= True
		conn = sqlite3.connect(self.DB_CONF['DB_name'])
		cur = conn.cursor()
		#print(libPath)
		#print(startDir)
		#print(engineMapDirLoc)

		# tempMap is file name of map
		for tempMap in tempMaps:
			if not tempMap.endswith('.png'):	
				# move current map file to `engine/maps`
				#os.chdir(startDir)
				#print(os.getcwd())
				#tmpMapLoc = os.path.join(tmp, tempMap)
				#engineMapLoc = os.path.join(engineMapDirLoc, tempMap)
				#targetMapLoc = os.path.join(target, tempMap)
				shutil.copy(self.startDir+'/tmpMap/'+tempMap, self.startDir+'/engine/maps/')
				# reinit unitsync everytime
				uSync.reinit()
				try:
						mapName = uSync.getMapName()
						minimapPath=uSync.storeMinimap(mapName)
						print(colored('[INFO]', 'green'), "Generated info for map "+str(os.listdir(self.startDir+'/engine/maps/'))+' minimap stored in '+ minimapPath, end = "\r")
						#minimapPath = 
				except:
						print(colored('[ERRO]', 'red'), "Invalid Map "+str(os.listdir(self.startDir+'/engine/maps/')))
						os.system('rm '+self.startDir+'/engine/maps/*')
						os.system('rm '+self.startDir+'/tmpMap/'+tempMap)
						continue
					
				
				#print(minimapPath)
				minimapFilename = minimapPath.split('/')[-1]
				minimapIpfsAddr = DFS.add2fs(minimapPath, minimapFilename)
				mapIpfsAddr = DFS.add2fs(self.startDir+'/tmpMap/'+tempMap, tempMap)
				mapHash = self._hashFile(self.startDir+'/tmpMap/'+tempMap)
				try:
					cur.execute("DELETE FROM maps WHERE map_name='"+mapName.replace(' ', '🦔')+"'")
					conn.commit()
				except:
					print('New map, no old rec '+mapName)
					
				cur.execute('INSERT INTO maps \
							(map_name, map_filename, minimap_filename, map_hash, minimap_ipfs_addr, map_ipfs_addr) \
							values (?, ?, ?, ?, ?, ?)',
							(mapName.replace(' ', '🦔'), tempMap, minimapFilename, mapHash, minimapIpfsAddr, mapIpfsAddr))
				os.system('rm '+self.startDir+'/engine/maps/*')
				# after finishing, move file to `finalMap/`
				#shutil.move(engineMapLoc, targetMapLoc)   finalMap is now a symlink to tmpMap, the server is running out of space

				conn.commit()
		#print(colored('[INFO]', 'green'), 'map updated')


	def updateArchive(self,archiveDir='/opt/archives'):
		with open("/opt/archives/path.json") as json_file:
			pathData = json.load(json_file)
			DFS = DntpFileSystem(mapDir='/archives')

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
				#if not os.path.isfile(archive):
					#continue
				if archive.endswith('.json'):
					print(colored('[INFO]', 'green'), 'skipping json'+archive)
					continue
						
				#archiveLoc = os.path.join(archiveDir, archive)
				try:
					archiveHash = self._hashFile(archiveDir+'/'+archive)
					print(colored('[INFO]', 'green'), 'got hash for archives'+archive)
				except:
					continue
				ipfs_addr = DFS.add2fs(archiveDir+'/'+archive, archive)
				try:
					cur.execute('INSERT INTO archives \
					(zip_name, extract_to, zip_hash, ipfs_addr) \
					values \
					(?, ?, ?, ?)', 
					(archive, pathData[archive], archiveHash, ipfs_addr))
					print(colored('[INFO]', 'green'), 'write hashdb for archives'+archive)
				except:
					print('undocumented files '+ archive)
				
				conn.commit()
			#print(colored('[INFO]', 'green'), 'updated archives')


	def _hashFile(self,file_path):
		"""_hashFile.
		fed with file_path return 32 chars md5 hash

		:param file_path:
		"""
		
		with open(file_path, 'rb') as f:
			toHash = f.read()

		return hashlib.md5(toHash).hexdigest()
				

	def getDirList(self,start_loc, ignore_pat=re.compile('(^\.)|(^__)')):
		res = []

		dirQueue = queue.Queue()
		dirQueue.put(start_loc)

		res = []
		while not dirQueue.empty():
			curDir = dirQueue.get()
			res.append(curDir)

			children = os.listdir(curDir)
			for child in children:
				curChild = os.path.join(curDir, child)
				if not re.match(ignore_pat, child) and os.path.isdir(curChild):
					dirQueue.put(curChild)

		return res


	def getFilelist(self,start_loc, ignore_pat=re.compile('(^\.)|(^__)')):
		"""getFilelist.

		:param start_loc: list all files under start_loc
		:param ignore_pat: ignore all matches this regex pattern
		"""
		if not os.path.exists(start_loc) and not os.path.isdir(start_loc):
			print(colored('[ERRO]', 'red'), 'start location ', start_loc, ' illegal.')
			return []

		dirQueue = queue.Queue()
		dirQueue.put(start_loc)

		res = []
		while not dirQueue.empty():
			curDir = dirQueue.get()
			children = os.listdir(curDir)
			for child in children:
				curChild = os.path.join(curDir, child)
				if not re.match(ignore_pat, child):
					if os.path.isdir(curChild):
						dirQueue.put(curChild)

					if os.path.isfile(curChild):
						res.append({'filename': child, 'path': curChild})

		return res

if __name__ == '__main__':
	pass
