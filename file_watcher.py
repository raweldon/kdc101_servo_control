import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print'event type: {} path: {}'.format(event.event_type, event.src_path)

def watch_file(directory):

    event_handler = MyHandler()
    observer = PollingObserver()
    observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()

    print 'watching for changes to', directory
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    directory = '\\\\VBOXSVR/count_rate_analysis/'
    watch_file(directory)