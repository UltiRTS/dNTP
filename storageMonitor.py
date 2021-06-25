import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from store import fileStorager
  
class OnMyWatch(threading.Thread):
    # Set the directory on watch
    watchDirectory = "/opt/archives"
  
    def __init__(self):
        super(OnMyWatch, self).__init__()
        self.observer = Observer()
        
        #self.store=fileStorager()
  
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")
  
        self.observer.join()
  
  
class Handler(FileSystemEventHandler):
  
    @staticmethod
    def on_any_event(event):
        store=fileStorager()
        if event.is_directory:
            return None
  
        elif event.event_type == 'created':
            # Event is created, you can process it now
            store.updateArchive()

              
  
if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
