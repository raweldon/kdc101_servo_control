import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print'event type: {} path: {}'.format(event.event_type, event.src_path)

if __name__ == '__main__':
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='C:/Users/radians/daf_2019/kdc101_kinesis_codes/', recursive=False)

    cnt = 1
    cnt1 = 1
    try:
        while True:
            time.sleep(1)
            cnt += 1
            if cnt == cnt1*10:
                cnt1 += 1
                print 'no change'
    except KeyboardInterrupt:
        observer.stop()
    observer.join()