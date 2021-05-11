import os
import libarchive



from unitSync import UnitSync


def buildIndex():
	 
	arr = os.listdir('maps')

	os.system('echo "" > maps/index.txt')
	startDir = os.getcwd()
	smf_fileName={} #gen by this py
	smf_realName={} #gen by usync
	finalIndex={}
	
	for i in arr:
		#if i.endswith('.sd7'):
			#archive = py7zr.SevenZipFile('maps/'+i, mode='r',decode='utf-8')
			#zContents = archive.getnames()
			#for zContent in zContents:
				#if zContent.endswith('.smf'):
					#smf_fileName[zContent.replace(' ', '🦔')]=i.replace(' ', '🦔')
		try:
			
			with libarchive.file_reader('maps/'+i) as e:

				for entry in e:
					#print(entry)
        # (The entry evaluates to a filename.)
					if str(entry).endswith('.smf'):
						smf_fileName[str(entry).replace(' ', '🦔')]=i.replace(' ', '🦔')
		except:
			print('skipping '+i)
			pass

			
		#elif i.endswith('sdz'):
			#zipContents = zipfile.ZipFile('maps/'+i)
			#for zipContent in zipContents.namelist():
				#if zipContent.endswith('.smf'):
					#smf_fileName[zipContent.replace(' ', '🦔')]=i.replace(' ', '🦔')
			
				#except:
					#if not str(i)=='redacted':
						#os.system('mv -f maps/'+i+' maps/redacted/')
					#print(i)
					#pass
					
	#print(smf_fileName)
	usync=UnitSync(startDir,startDir+'/engine/libunitsync.so')
	smf_realName=usync.mapNameVSMapFileName()
	#print (smf_realName)
	for smf in smf_fileName:   #this loop establishes association between real name and file names
		try:
			#everyMapName
			#print (smf_realName[smf])
			#print (smf_fileName[smf])
			finalIndex[smf_realName[smf]]=smf_fileName[smf]
		except:
			print('usync excluding '+smf)
			pass
			#print(smf_fileName[smf])
			#print(smf_fileName)
			#print('bad maps '+smf)
			#os.system('mv -f maps/'+i+' maps/redacted/')
	#print(finalIndex)	
	totalItems=0
	for items in finalIndex:
		totalItems=totalItems+1
	print('totalMaps: '+str(totalItems))	
	
	
	
	arr = os.listdir('maps')
	#os.system('echo "'+str(arr)+' " > maps/allMaps.txt')	
	for everyFreakingFile in arr:
		for everyMapName in finalIndex:
			if everyFreakingFile == finalIndex[everyMapName]:
				#os.system('echo "'+everyMapName+' '+everyFreakingFile+' " >> maps/index.txt')
				ret_code = os.system('echo "'+everyMapName+' '+everyFreakingFile+' " >> maps/index.txt')
				print(ret_code, 'echo "'+everyMapName+' '+everyFreakingFile+' " >> maps/index.txt')
				if everyFreakingFile == '1944_titan.sd7':
					print('!!!!!!!!!!freaking titan will be perserved!')
					print(ret_code)
				
				break
		else:
			if not everyFreakingFile.endswith('redacted'):
				os.system('mv -f "maps/'+everyFreakingFile.replace('🦔', ' ')+'" maps/redacted/')
				
				#if everyFreakingFile == '1944_titan.sd7':
				#	print('!!!!!!!!!!freaking titan will be removed!')
		
	#print (finalIndex)
		
	#print (finalIndex)
	#print(smf_fileName)
	#print(str(smf_realName)+'aaaaa')
	return finalIndex
		
		

		
		
if __name__ == '__main__':
	buildIndex()
