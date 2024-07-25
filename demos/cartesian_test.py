### This is a simple demo script using the Cartesian pose planning. 
### Just verify the robot is calibrated, in position control mode and connected
### with roslibpy, then running this script will just cycle through some motions

import sys
import time

import roslibpy

try:
    # Connect to the Pi's rosbridge server over port 9090
    client = roslibpy.Ros(host='192.168.100.3', port=9090) # The host needs to be changed to the correcet Pi address
    client.run()

    if not client.is_connected:
        print('Cannot connect to roslibpy server')
        sys.exit()
    if not ('/tendon_transmission_node/commands' in client.get_topics()):
        print('Tendon command topic not available')
        sys.exit()
    if not ('/helix_cartesian_control_node/delta_increment' in client.get_topics()):
        print('Cartesian control not available')
        sys.exit()

    # Reset the model and robot to calibrated zero position
    reset_srv = roslibpy.Service(
        client, '/helix_cartesian_control_node/reset_model', 
        'std_srvs/Trigger')
    reset_req = roslibpy.ServiceRequest()
    result = reset_srv.call(reset_req)

    goto_srv = roslibpy.Service(
        client, '/helix_cartesian_control_node/go_to_gripper_pose_vector', 
        'helix_transmission_interfaces/GoToGripperPoseVector')

    # Loop through until keyboard interrupt
    while(True):
        
        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": 0, "y": 0, "z": -0.5},
            "goal_direction":{"x": 0, "y": 0, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1)

        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": 0.17, "y": 0, "z": -0.5},
            "goal_direction":{"x": 0, "y": 0, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1)
        
        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": -0.17, "y": 0, "z": -0.5},
            "goal_direction":{"x": 0, "y": 0, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1.5)

        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": 0, "y": 0.17, "z": -0.5},
            "goal_direction":{"x": 0, "y": 0, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1)

        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": 0, "y": -0.17, "z": -0.5},
            "goal_direction":{"x": 0, "y": 0, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1)

        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": 0, "y": -0.17, "z": -0.5},
            "goal_direction":{"x": 0, "y": -1, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1.5)

        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": 0, "y": -0.1, "z": -0.43},
            "goal_direction":{"x": 0, "y": -1, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1)

        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": -0.15, "y": -0.1, "z": -0.43},
            "goal_direction":{"x": 0, "y": -1, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1)
        
        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": -0.15, "y": -0.1, "z": -0.5},
            "goal_direction":{"x": 0, "y": -1, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(0.5)

        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": -0.15, "y": -0.1, "z": -0.5},
            "goal_direction":{"x": -1, "y": 0, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1.5)

        goto_req = roslibpy.ServiceRequest({
            "goal_point":{"x": -0.15, "y": -0.1, "z": -0.5},
            "goal_direction":{"x": 0, "y": 0, "z": -1},
            "plan_linear":True
            })
        result = goto_srv.call(goto_req)
        time.sleep(1.5)

except(SystemExit, KeyboardInterrupt):
    print('Terminating roslibpy client')
    client.terminate()