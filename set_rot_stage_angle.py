"""
This example shows how to communicate with Thorlabs KDC101, KCube DC Servo.
"""

import os
from pprint import pprint
from msl.equipment import EquipmentRecord, ConnectionRecord, Backend

# ensure that the Kinesis folder is available on PATH
os.environ['PATH'] += os.pathsep + 'C:/Program Files/Thorlabs/Kinesis'

# rather than reading the EquipmentRecord from a database we can create it manually
record = EquipmentRecord(
    manufacturer='Thorlabs',
    model='KDC101',
    serial='27002424',  # update the serial number for your KDC101
    connection=ConnectionRecord(
        backend=Backend.MSL,
        address='SDK::Thorlabs.MotionControl.KCube.DCServo.dll',
    ),
)

def wait(value, motor):
    motor.clear_message_queue()
    message_type, message_id, _ = motor.wait_for_message()

def home_stage(ang_pos, pos, motor):
    print('Homing...')
    motor.home()
    wait(0, motor)
    print('Homing done. Stage at {} deg, {} device units'.format(ang_pos, pos))

def main():

    # connect to the KCube DC Servo
    motor = record.connect()
    print('\nConnected to {}\n'.format(motor))

    # load the configuration settings (so that we can use the get_real_value_from_device_unit() method)
    motor.load_settings()

    # check if stage needs to be homed
    position = motor.get_position()
    ang_pos = motor.get_real_value_from_device_unit(position, 'DISTANCE')
    if motor.can_move_without_homing_first():
        print('Stage is homed')
    else:
        print('Stage is not homed')
        home_stage(ang_pos, position, motor)

    new_position = 120
    np = motor.get_device_unit_from_real_value(new_position, 'DISTANCE')
    motor.move_to_position(np)
    wait(1, motor)
    print('rotated to {}'.format(motor.get_real_value_from_device_unit(motor.get_position(), 'DISTANCE')))

if __name__ == '__main__':
    main()    

