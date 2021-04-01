import os
from zkscrapper import zkScrap
from springCrapper import SpringCrapper

if not os.path.exists('maps'):
    os.makedirs('maps')

zk=zkScrap()
zk.start()

sc = SpringCrapper()
sc.start()