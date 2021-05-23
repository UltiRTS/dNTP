import os
import libarchive



from unitSync import UnitSync


def buildIndex():
	startDir = os.getcwd()
	os.system('echo "" > finalMap/index.txt')
	arr = os.listdir('tmpMap')
	totalMaps=0
	failedMaps=0
	os.system('rm -rf engine/maps/*')
	for i in arr:
		totalMaps+=1
		os.system('cp -a "tmpMap/'+i+'" engine/maps/')
		usync=UnitSync(startDir,startDir+'/engine/libunitsync.so')
		#init=usync.init()
		
		
		try:
			mapName=usync.getMapName()
			usync.storeMinimap(mapName)
			os.system('echo "'+mapName.replace(' ', '🦔')+' '+i.replace(' ', '🦔')+'" >> finalMap/index.txt')
			os.system('mv -f engine/maps/* finalMap/')
			print('[dNTP] Generated minimaps for'+str(i)+' ('+str(totalMaps)+')')
		
		except Exception as e:
			failedMaps+=1
			print(e)
			os.system('rm -rf engine/maps/*')
			
			
		
		#os.system('rm -rf engine/maps/*')
		
	print('dNTP completed; totalmaps: '+str(totalMaps)+' failed maps: '+ str(failedMaps))
	
	
	
	

	
	

		
		

		
		
if __name__ == '__main__':
	buildIndex()
