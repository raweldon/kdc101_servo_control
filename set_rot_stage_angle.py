"""
Communicate with Thorlabs KDC101, KCube DC Servo.
"""

import os
from pprint import pprint
from msl.equipment import EquipmentRecord, ConnectionRecord, Backend
from types import MethodType
import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler

def motor_startup():
    # ensure that the Kinesis folder is available on PATH
    os.environ['PATH'] += os.pathsep + 'C:/Program Files/Thorlabs/Kinesis'

    # rather than reading the EquipmentRecord from a database we can create it manually
    record = EquipmentRecord(
        manufacturer='Thorlabs',
        model='KDC101',
        serial='27002424',  # update the serial number for your KDC101
        connection=ConnectionRecord(
            backend=Backend.MSL,
            address='SDK::Thorlabs.MotionControl.KCube.DCServo.dll'))

    # connect to the KCube DC Servo
    motor = record.connect()
    print('\nConnected to {}'.format(motor))

    # load the configuration settings (so that we can use the get_real_value_from_device_unit() method)
    motor.load_settings()
    return motor

def wait(value, motor):
    motor.clear_message_queue()
    message_type, message_id, _ = motor.wait_for_message()

def home_stage(motor):
    # check if stage needs to be homed and home if needed
    position = motor.get_position()
    ang_pos = motor.get_real_value_from_device_unit(position, 'DISTANCE')
    if motor.can_move_without_homing_first():
        print('\nStage is homed')
    else:
        print('\nStage is not homed')
        print('    Homing...')
        motor.home()
        wait(0, motor)
        print('    Homing done. Stage at {} deg, {} device units'.format(ang_pos, position))

def read_file(directory, filename):
    with open(directory + filename) as f:
        line = f.readlines()
        line = [float(x) for x in line]
    return line[0]

def update_position(new_ang, motor):
    new_position = motor.get_device_unit_from_real_value(new_ang, 'DISTANCE')
    motor.move_to_position(new_position)
    wait(1, motor)
    print('rotated to {}'.format(motor.get_real_value_from_device_unit(motor.get_position(), 'DISTANCE')))
    print('-------------------------------------------------------------------------------------')

def start_up(directory, filename, motor):
    ''' home stage and read first text file setting '''
    home_stage(motor)
    start_angle = read_file(directory, filename)
    return start_angle

### Watchdog
class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.txt"]

    def __init__(self, observer):
        super(MyHandler, self).__init__(self)
        #object.__init__(self)
        self.observer = observer

    def on_modified(self, event):
        print('event occured of type: {} path: {}'.format(event.event_type, event.src_path))
        self.observer.stop()
        print('watchdog stopped')

def watch_file(directory, filename):
    observer = PollingObserver()
    observer.schedule(MyHandler(observer), path=directory)
    observer.start()

    print('\nwatching for changes to {}'.format(directory))
    while observer.isAlive() == True:
        time.sleep(1)

    observer.join()
###

def main():
    directory = '\\\\VBOXSVR/count_rate_analysis/' # vm share directory
    filename = 'rot_angle.txt'

    motor = motor_startup()

    # get starting angle
    start_angle = start_up(directory, filename, motor)
    update_position(start_angle, motor)

    # start watch
    old_ang = 0
    try:
        while True:
            watch_file(directory, filename)
            new_ang = read_file(directory, filename)
            if new_ang == old_ang:
                print('   no change in angle was detected\n    rotational stage is still at {}'.format(new_ang))
                continue
            update_position(new_ang, motor)
            old_ang = new_ang
    except KeyboardInterrupt:
        print('\nmeasurement terminated\n')

if __name__ == '__main__':
    main()    

