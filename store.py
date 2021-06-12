import os
import re
import queue
import sqlite3
import hashlib
from termcolor import colored
from dntpFilesystem import DntpFileSystem
from unitSync import UnitSync

DB_CONF = {
        'DB_name': 'info.db',
        'schema_loc': 'schema.sql'
}

def initDB(database_name=DB_CONF['DB_name'], schema_loc=DB_CONF['schema_loc']):

    conn = sqlite3.connect(database_name);
    cur = conn.cursor()

    with open(schema_loc, 'r') as fp:
        cur.executescript(fp.read())
        conn.commit()
    
    print(colored('[INFO]', 'green'), 'Initialized db')


def updateEngine(engine_loc='engine'):

    DFS = DntpFileSystem(mapDir='/engine')
    filelist = getFilelist(engine_loc)
    dirlist = getDirList(engine_loc)

    DFS.mkdirs(dirlist)

    conn = sqlite3.connect(DB_CONF['DB_name'])
    cur = conn.cursor()

    for i in range(len(filelist)):
        fileInfo = filelist[i]

        ipfs_store_loc = '/' + fileInfo['path'].split(fileInfo['filename'])[0]
        ipfs_addr = DFS.add2fs(fileInfo['path'], fileInfo['filename'], ipfs_store_loc)

        filelist[i]['ipfs_addr'] = ipfs_addr
        filelist[i]['md5'] = hashFile(fileInfo['path'])

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


def getDirList(start_loc, ignore_pat=re.compile('(^\.)|(^__)')):
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


def getFilelist(start_loc, ignore_pat=re.compile('(^\.)|(^__)')):
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

    
def updateMaps(tmp='tmpMap', target='finalMap', engineLoc='engine'):

    DFS = DntpFileSystem(mapDir='/maps')

    libPath = os.path.join(engineLoc, 'libunitsync.so')
    uSync = UnitSync(os.getcwd(), libPath)

    tempMaps = os.listdir(tmp)
    engineMapDirLoc = os.path.join(engineLoc, 'maps')

    conn = sqlite3.connect(DB_CONF['DB_name'])
    cur = conn.cursor()

    # tempMap is file name of map
    for tempMap in tempMaps:

        # reinit unitsync everytime
        uSync.reinit()

        tmpMapLoc = os.path.join(tmp, tempMap)
        engineMapLoc = os.path.join(engineMapDirLoc, tempMap)
        targetMapLoc = os.path.join(target, tempMap)

        # move current map file to `engine/maps`
        os.rename(tmpMapLoc, engineMapLoc)

        mapName = uSync.getMapName()
        minimapPath = uSync.storeMinimap(mapName)
        minimapFilename = minimapPath.split('/')[-1]
        minimapIpfsAddr = DFS.add2fs(minimapPath, minimapFilename)
        mapIpfsAddr = DFS.add2fs(engineMapLoc, tempMap)
        mapHash = hashFile(engineMapLoc)

        cur.execute('INSERT INTO maps \
                    (map_name, map_filename, minimap_filename, map_hash, minimap_ipfs_addr, map_ipfs_addr) \
                    values (?, ?, ?, ?, ?, ?)',
                    (mapName, tempMap, minimapFilename, mapHash, minimapIpfsAddr, mapIpfsAddr))
        
        # after finishing, move file to `finalMap/`
        os.rename(engineMapLoc, targetMapLoc)

    conn.commit()
    print(colored('[INFO]', 'green'), 'map updated')

def hashFile(file_path):
    """hashFile.
    fed with file_path return 32 chars md5 hash

    :param file_path:
    """
    with open(file_path, 'rb') as f:
        toHash = f.read()

    return hashlib.md5(toHash).hexdigest()

def updateArchive(archiveDir='/opt/archive'):

    DFS = DntpFileSystem(mapDir='/archives')

    conn = sqlite3.connect(DB_CONF['DB_name'])
    cur = conn.cursor()

    archives = os.listdir(archiveDir)

    for archive in archives:
        if not os.path.isfile(archive):
            continue
            
        archiveLoc = os.path.join(archiveDir, archive)
        archiveHash = hashFile(archiveLoc)
        ipfs_addr = DFS.add2fs(archiveLoc, archive)

        cur.execute('INSERT INTO archives \
            (zip_name, extract_to, zip_hash, ipfs_addr) \
            values \
            (?, ?, ?, ?)', 
            archive, archive, archiveHash, ipfs_addr)
        
    conn.commit()
    print(colored('[INFO]', 'green'), 'updated archives')

            
            

if __name__ == '__main__':
    initDB()

    updateMaps()