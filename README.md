# I want to set up a new robot/RPi

## Initial Pi configuration steps
- Ideally begin with a clean OS image (Rasperry Pi OS Lite recommended)
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
 - In `main`, run `$ docker compose up` to start everything up at once.
 - If you want the output to be more readable, containers can be started selectively in separate terminals. For example, in one terminal `$ docker compose up nginx studio ros-foxglove-bridge ros-rosbridge-suite` and in another one: `$ docker compose up ros-helix`. This will provide a separate cleaner output for the motor controller container, useful for troubleshooting.
- If the below messages are printed when starting the `ros-helix` container, everything should be working:
```
Loaded motor_head_joint_position_controller (in blue)
Configured and activated motor_head_joint_position_controller (in green)
Loaded motor_head_joint_state_broadcaster (in blue)
Configured and activated motor_head_joint_state_broadcaster (in green)
Loaded motor_head_joint_effort_controller (in blue)
```
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

# I want to control the robot from Python, Foxglove or ROS
Assuming the Pi has already been set up as above, see the instructions in the [ros-helix repo](https://github.com/helix-robotics-ag/ros-helix/tree/main) README.

# I want to develop code inside these repositories to run on the robot controller itself
Note: this is not particularly straightforward, if you only need to access the robot state and send commands, consider doing it externally through `roslibpy`. If you're sure it needs to be incorporated into the embedded system, it may still be easier to prototype something externally first as well. A reasonable familiarity with ROS2 and git are prerequisite, as well as some understanding of Docker.

## Where do I put my code?
Depending on what you're doing, this is probably something to discuss with the project team. As it stands there are currently two main places where the actual 'robot control' code goes: the public `ros-helix` repo, which contains the basic robot description and motor controllers, and `ros-helix-proprietary`, which is for anything that should be private. `ros-rosbridge-suite` and `ros-foxglove-bridge` are just used to expose the ROS system to other interfaces, and don't need to be modified unless new dependencies are required (such as custom message types).

## Git submodule setup
This `main` repo includes others as git [submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), which you should read about. Without reproducing all of the documentation, some of the important points to understand are:
- When submodule repos are included, the parent repo (this one, `main`), doesn't track all of the files in them as if they were copied there. It only keeps track of which commit is checked out in the submodule as part of `main`'s state. Checking out a different commit in a submodule will appear as a change in `main`, and uncommitted changes in a submodule will additionally flag the change as 'dirty'.
- To make sure all of your local repos are up to date, you should run `$ git submodule update --init --recursive` after cloning `main`, which will cause all the submodules to check out the commits tracked by `main`'s current state (recursively, in case any submodules have their own submodules). Later, after pulling new changes to `main`, you will need to run the same command again to update the submodules (`--init` is only needed if new submodules have been added as a result of changes to `main`, but doesn't hurt to include anyway).
- When you merge your own changes into a submodule, you then need to go into the `main` repo, check out your new commit in the submodule, and commit this as a new change to the `main` repo. Otherwise, the state of `main` still points to the previous commit in the submodule, before your changes.
There are other ways to handle all of this, which you can read about in the git documentation.

## Container setup
This repo contains a `docker-compose-yml` file, which allows for a user to simply run `docker compose up` in order to launch all the required containers from the remotely built images, and with the standard configurations. To develop the code, you need to know more about how these containers are configured and built, as well as how to more efficiently change and build them locally.
