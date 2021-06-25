import os

import threading

  
class ipfs(threading.Thread):

  
    def __init__(self):
        super(ipfs, self).__init__()
        
  
    def run(self):
        os.system('ipfs daemon')
  

