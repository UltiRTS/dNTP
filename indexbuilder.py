import os
import py7zr
import zipfile
from unitSync import UnitSync
def buildIndex():
	 
	import os
import py7zr
import zipfile
from unitSync import UnitSync
def buildIndex():
	 
	arr = os.listdir('maps')

	os.system('echo "" > maps/index.txt')
	startDir = os.getcwd()
	smf_fileName={} #gen by this py
	smf_realName={} #gen by usync
	finalIndex={}
	
	for i in arr:
		if not i.endswith('.txt'):
			try:
				archive = py7zr.SevenZipFile('maps/'+i, mode='r')
				zContents = archive.getnames()
				for zContent in zContents:
					if zContent.endswith('.smf'):
						smf_fileName[zContent.replace(' ', '🦔')]=i.replace(' ', '🦔')
			
			except:
				try:
					zipContents = zipfile.ZipFile('maps/'+i)
					for zipContent in zipContents.namelist():
						if zipContent.endswith('.smf'):
							smf_fileName[zipContent.replace(' ', '🦔')]=i.replace(' ', '🦔')
			
				except:
				#os.system('rm -rf maps/'+i)
					print(i)
					
	
	usync=UnitSync(startDir,startDir+'/engine/libunitsync.so')
	smf_realName=usync.mapNameVSMapFileName()
	#print (smf_realName)
	for smf in smf_realName:
		try:
			os.system('echo "'+smf_realName[smf]+' '+smf_fileName[smf]+' " >> maps/index.txt')
			#print (smf_realName[smf])
			#print (smf_fileName[smf])
			finalIndex[smf_realName[smf]]=smf_fileName[smf]
		except:
			#pass
			#print(smf_fileName[smf])
			#print(smf_fileName)
			print('bad maps '+smf)
		
	#print (finalIndex)
		
	print (finalIndex)
	#print(smf_fileName)
	#print(str(smf_realName)+'aaaaa')
	return finalIndex
		
		

		
		
if __name__ == '__main__':
	buildIndex()
