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

# I want to control the robot from ROS, Foxglove or Python
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

### What happens when a container is launched normally
Since the `main` repo is just used to combine the launch files and doesn't define a container itself, we will refer to the `ros-helix` repository as a full example. Starting with the `docker-compose.yml` file in that repo, we can see that launching a container using it (such as with `docker compose up` from the `main` or `ros-helix` repo) will use an image hosted on `ghcr.io`. Without going into detail, this image is built remotely whenever a push to the `main` branch of `ros-helix` occurs - see `.github/workflows/ci.yml`. Other details defined in this compose configuration file include: specifying the `Dockerfile` in the repo will be used to build the container; settings to share networking and ports with the host; some environment variables and volume mounts; and finally the command that will run when the container starts. To understand what the startup command does, we will first need to review the build process for the container image, defined by the `Dockerfile`.

### What happens when the container image is built
As specified in `docker-compose.yml`, the file `Dockerfile` defines the build process. There are several stages to the build:
- Firstly, a minimal `ros-core` image is used as a base to start from
- Next, a range of additional packages are installed, including some standard ROS tools and message definitions, as well as more specific dependencies (such as `ros2-control` and `dynamixel-workbench-toolbox` for the `ros-helix` container)
- Next, the `ros-entrypoint.sh` script is copied from the repo into the container image. Note that executing this script on startup is inherited from [the base ROS image](https://github.com/osrf/docker_images/blob/27cc0b68263bbbb10bb58dd814efc0a6b0a01ec7/ros/iron/ubuntu/jammy/ros-core/Dockerfile#L45). Aside from sourcing the ROS installaion `setup.bash`, this script also creates a user `ros`, with a UID that may be inherited from a host environment variable.
- Next, the source code from the repo is copied into a colcon workspace in the container image, where it is built and sourced. The next line creates a shortcut for building the colcon workspace when inside the container.
- The second to last line writes some commands to the shell script `/run.sh`, which defines the standard startup behaviour of the container. For `ros-helix`, this is to source the required installation paths, then run a launch file: `ros2 launch helix_bringup helix_bringup.launch.py`.
- The final line also creates a shortcut, this time to execute the `/run.sh` script as the user `ros`. Note that this is the same command used in the `docker-compose.yml` file.

Having examined the above, we can now see that when running `docker compose up`, a container will start using the remotely built image and configured as in `docker-compose-yml`. Once it is created, a command will be run inside the container which switches to the `ros` user (who has previously been defined in the `ros_entrypoint.sh` script) and executes the `/run.sh` script, which is where the actual nodes we want to run inside the container are launched.

### How to make and test changes
Important note: you should always create a new branch to make and test changes on, not commit or push changes directly to the `main` branch (in fact, you will usually not be able to do this without creating a pull request that needs to be reviewed).

If you make changes to the source code in the repositories locally, then launch the containers using the remotely built images, nothing will change, since the container image is based on the code that was last pushed to the `main` branch. Instead, you could rebuild the image locally (run the `build.sh` script in the repo, or just do `docker compose build`) so that your local source code is copied in during the build process. This will work, but building the whole image can take a long time, especially if you are developing directly on a Pi. 

An alternative way to test changes more efficiently is to use the `run.sh` script in the repository (note that this is completely separate from the `run.sh` script that exists __inside__ the container). Executing this script will start the container using the same `docker-compose.yml` configuration, with two differences compared to just using `docker compose up`:
- The source code directories in the repository will be mounted into the colcon workspace in the container (ie, it will overwrite the files that were copied in when the image was built). Note that mounted in the container this way, the directories are shared with the host, so changes made on the host will be reflected in the (running) container and vice versa.
- The command defined in `docker-compose.yml` is overwritten. Instead you will be presented with a terminal inside the container, conveniently in the `colcon_ws` directory. From here you can use the `build` alias to build the modified source code, and the `run` alias to execute the normal startup command. In this way you can test the code, stop it, make changes on the host, rebuild the source code only, and retest it, in an efficient loop and without having to close or rebuild the container image.
