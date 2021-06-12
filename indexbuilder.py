import os
import shutil
from unitSync import UnitSync
from dntpFilesystem import DntpFileSystem

DFS = DntpFileSystem()

def buildIndex():
	mapsInfo = []

	startDir = os.getcwd()
	os.system('echo "" > finalMap/index.txt')
	arr = os.listdir('tmpMap')
	totalMaps=0
	failedMaps=0
	os.system('rm -rf engine/maps/*')

	usync=UnitSync(startDir,startDir+'/engine/libunitsync.so')
	for i in arr:
		totalMaps+=1
		os.system('cp -a "tmpMap/'+i+'" engine/maps/')
		#init=usync.init()
		usync.reinit()
		
		try:
			mapName=usync.getMapName()
			mapFileName=usync._getMapFileName(0)
			mapArciveName = usync._getMapArchiveName(mapName)
			minimapPath = usync.storeMinimap(mapName)
			minimapFilename = minimapPath.split('/')[-1]

			ipfs_addr = DFS.add2fs(minimapPath, minimapFilename)

			
			os.system('echo "'+mapName.replace(' ', '🦔')+' '+i.replace(' ', '🦔')+'" >> finalMap/index.txt')
			os.system('mv -f engine/maps/* finalMap/')

			print('[dNTP] Generated minimaps for'+str(i)+' ('+str(totalMaps)+')')
		
		except Exception as e:
			failedMaps+=1
			print(e)
			os.system('rm -rf engine/maps/*')
			
			
		
		#os.system('rm -rf engine/maps/*')
		
	print('dNTP completed; totalmaps: '+str(totalMaps)+' failed maps: '+ str(failedMaps))

	return mapsInfo
	
	
	
if __name__ == '__main__':
	buildIndex()
