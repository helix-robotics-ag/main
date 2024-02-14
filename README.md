# Run on Pi
## Setup
- Install docker on the Pi - most easily with the [script](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script), including the [post-install steps](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) mentioned under **'Use Docker as a non-privileged user...'**.
- Make sure you can authenticate on github (eg set up SSH key on the Pi)
- [Copy the rules file](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_workbench/#copy-rules-file) for Dynamixel Workbench
## Clone repo/submodules
- Clone this repo
- In the repo, initialise and update all its submodules recursively:
```
$ cd main/
$ git submodule update --init --recursive
```
 ## Start up the controllers
 - In a perfect world, you can now do `$ docker compose up` and everything will start up (note: the motors might make a full turn on start up, make sure the tendons aren't already overly tight)
 - In the real world, Dynamixel Workbench and the USB connection is currently a bit unstable, and might require a few tries to work. To make the output a bit more readable, start all the other containers in one terminal: `$ docker compose up nginx studio ros-foxglove-bridge ros-rosbridge-suite` and the motor controller container in a separate one: `$ docker compose up ros-helix`
 - There might be a lot of output as the `ros-helix` container starts up, if there are red 'controller failed to activate' messages or continuous streams of errors, shut it down and try again
 - If the below four messages are printed, everything should be working:
```
Loaded motor_head_joint_position_controller (in blue)
Configured and activated motor_head_joint_position_controller (in green)
Loaded motor_head_joint_state_broadcaster (in blue)
Configured and activated motor_head_joint_state_broadcaster (in green)
```
(Note there may still be some errors such as `[DynamixelHardware]: groupSyncRead getdata failed`, this is ok as long as they're not being printed continuously)
## Test reading and sending commands
- In roslibpy with [the test script](https://github.com/fstella97/HelixRobotics/blob/main/ROS/roslibpy_test.py)
- In foxglove studio: use a broswer to go to `<IP_of_Pi>:8080`, choose 'Open Connection' and use `ws://<IP_of_Pi>:8765`
