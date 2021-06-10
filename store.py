import os
import sqlite3
import hashlib
from termcolor import colored
from dntpFilesystem import DntpFileSystem


def initDB(database_name='info.db', schema_loc='schema.sql'):

    conn = sqlite3.connect(database_name);
    cur = conn.cursor()

    with open(schema_loc, 'r') as fp:
        cur.executescript(fp.read())
        conn.commit()
    
    print(colored('[INFO]', 'green'), 'Initialized db')


def updateEngine(engine_loc):

    DFS = DntpFileSystem()
    filelist = getFilelist()
    pass

def getFilelist(start_loc):
    pass

def hashFile(file_path):
    with open(file_path, 'rb') as f:
        toHash = f.read()

    return hashlib.md5(toHash).hexdigest()


if __name__ == '__main__':
    initDB()
