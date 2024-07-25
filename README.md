# I want to set up a new robot/RPi

## Initial Pi configuration steps
- Ideally begin with a clean OS image (Rasperry Pi OS Lite recommended)
- If the user ID of the account (`$ id -u`) isn't `1000`, add `export HOST_UID=$UID` to the `~/.bashrc` file.
- Install docker - most easily with the [script](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script), including the [post-install steps](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) mentioned under **'Use Docker as a non-privileged user...'**.
- Make sure you can authenticate on github (eg set up an SSH key on the Pi)
- [Copy the rules file](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_workbench/#copy-rules-file) for Dynamixel Workbench
- Create the robot config folder on the Pi: `mkdir ~/.config/helix`

## Installing the Helix repos
- Clone this repo, for example into `~/helix-robotics-ag/`
- In the repo, initialise and update all its submodules recursively:
```
$ cd main/
$ git submodule update --init --recursive
```

 ## Start up the controllers
 - In `main`, run `$ docker compose pull` to pull the up to date docker images.
 - **NOTE:** There is currently an issue with authorisation for the `ros-helix-proprietary` image, you will probably see a warning/error about this and need to do `$ docker compose build ros-helix-proprietary` manually.
 - In `main`, run `$ docker compose up` to start up everything at once.
 - If you want the output to be more readable, containers can be started selectively in separate terminals. For example, in one terminal `$ docker compose up nginx studio ros-foxglove-bridge ros-rosbridge-suite` and in another one: `$ docker compose up ros-helix`. This will provide a separate cleaner output for the motor controller container, useful for troubleshooting.
- If some messages in green and blue saying 'Loaded...' and 'Configured...' the various controllers are printed when starting the `ros-helix` container, everything should be working.

## Troubleshooting
- If there are red error messages, continuous streams of errors, or inscrutable low level crash logs, things are probably not ok and should be restarted
- It may be sufficient to just stop the `ros-helix` container (`CTRL-C`) and then restart with `$ docker compose up ros-helix`.
- More thoroughly, you may want to close down the container properly and power cycle the motor controller:
    - `$ docker compose down ros-helix` in the `main` repo directory
    - Remove power from the motor controller (not the Pi), and unplug the USB connection from the controller to the Pi
    - Power the motor controller again, then plug in the USB again
    - Restart the container
    - Note that generally, it is fine to leave the other containers running (assuming the problem is with launching `ros-helix`)
- If problems launching persist, one thing to check is whether the `ttyUSB0` port is listed in the `/dev/` directory of the Pi. If it isn't there or the number isn't `0`, the controller definitely won't launch. However, ultimately the solution to this is still just power cycling/reconnecting the USB, or in the worst case, restarting the Pi itself.

## Dummy Mode
It is possible to run the system in 'dummy mode' for testing without connecting to the robot/motor hardware. To do this, follow the above installation instructions on your (linux) system, then uncomment the line `<param name="use_dummy">true</param>` in `/ros-helix/helix_description/urdf/helix.ros2_control.xacro`, and rebuild the `ros-helix` image: `$ docker compose build ros-helix`. In this mode, the system will not communicate with the motors, but will just update the motor joint states directly to the received commands. All other parts of the system should still work, you will just need to replace the Raspberry Pi's IP with `localhost` when using the Foxglove or `roslibpy` interface.

# I want to control the robot from ROS, Foxglove or Python
Assuming the Pi has already been set up as above, see the instructions in the [ros-helix repo](https://github.com/helix-robotics-ag/ros-helix/tree/main) README.

# I want to develop code inside these repositories to run on the robot controller itself
Note: this is not particularly straightforward, if you only need to access the robot state and send commands, consider doing it externally through `roslibpy`. If you're sure it needs to be incorporated into the embedded system, it may still be easier to prototype something externally first as well. A reasonable familiarity with ROS2 and git are prerequisite, as well as some understanding of Docker. For more information about the repos and containers, see the [separate guide](Devguide.md).