import os
import re
import queue
import sqlite3
import hashlib
from termcolor import colored
from dntpFilesystem import DntpFileSystem

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

    

def hashFile(file_path):
    """hashFile.
    fed with file_path return 32 chars md5 hash

    :param file_path:
    """
    with open(file_path, 'rb') as f:
        toHash = f.read()

    return hashlib.md5(toHash).hexdigest()


if __name__ == '__main__':
    initDB()

    updateEngine()
