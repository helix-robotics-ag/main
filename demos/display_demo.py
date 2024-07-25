### This is a simple demo script using a set of saved joint trajectories.
### Just verify the robot is calibrated, in position control mode and connected
### with roslibpy, then running this script will just cycle through some motions

import sys
import time
import csv

import roslibpy

tendon_positions = []
with open('./display_demo_tendon_positions.csv', 'r') as csvdata:
    csvreader = csv.reader(csvdata)
    for row in csvreader:
        positions = [float(joint) for joint in row]
        tendon_positions.append(positions)

try:
    # Connect to the Pi's rosbridge server over port 9090
    client = roslibpy.Ros(host='192.168.100.3', port=9090) # The host needs to be changed to the correcet Pi address
    client.run()

    if not client.is_connected:
        print('Cannot connect to roslibpy server')
        sys.exit()
    if not ('/tendon_transmission_node/tendon_states' in client.get_topics()):
        print('Tendon state topic not available')
        sys.exit()
    if not ('/tendon_transmission_node/commands' in client.get_topics()):
        print('Tendon command topic not available')
        sys.exit()

    listener = roslibpy.Topic(client, '/tendon_transmission_node/tendon_states', 'sensor_msgs/msg/JointState')
    talker = roslibpy.Topic(client, '/tendon_transmission_node/commands', 'std_msgs/msg/Float64MultiArray')

    # Loop through until keyboard interrupt
    while(True):
        for n in range(len(tendon_positions)):
            talker.publish(roslibpy.Message({'data': tendon_positions[n]}))
            time.sleep(0.02)
        time.sleep(4)

except(SystemExit, KeyboardInterrupt):
    print('Terminating roslibpy client')
    client.terminate()