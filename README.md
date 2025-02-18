# Habitat-ROS
A ROS wrapper for [Habitat-Sim](https://github.com/facebookresearch/habitat-sim). It allows getting RGB, depth and semantic renders from ROS. It also contains a simplified MAV simulator. It can load [Replica Dataset](https://github.com/facebookresearch/Replica-Dataset). and publish the RGB-D and tf.

## Build

### Install dependencies

Only tested on Ubuntu 20.04 and ROS Noetic. 

``` bash
sudo apt-get install -y --no-install-recommends libjpeg-dev libglm-dev \
    libgl1-mesa-glx libegl1-mesa-dev mesa-utils xorg-dev freeglut3-dev \
    python3-pip python3-attr python3-numba python3-numpy python3-pil \
    python3-scipy python3-tqdm python3-matplotlib python3-git
pip3 install --user numpy-quaternion
# The habitat-sim install script calls pip expecting pip3. The following command
# will fail if /usr/local/bin/pip exists.
sudo ln --symbolic /usr/bin/pip3 /usr/local/bin/pip
```

### Build package

This is a normal ROS package so all you have to do is create a workspace, clone the repository and build. This will build Habitat-Sim which will take some time and require a lot of RAM and CPU time.

``` bash
mkdir -p ~/catkin_ws/src/ && cd ~/catkin_ws/src/
source /opt/ros/noetic/setup.bash
catkin init
git clone https://github.com/ppppplus/habitat-ros.git
catkin build -DCMAKE_BUILD_TYPE=Release habitat_ros
```

## Dataset download

Get the Matterport3D download script from [here](https://niessner.github.io/Matterport/). 

``` bash
python3 download_mp.py --task habitat -o /path/to/download/
```
Get Replica Dataset from [here](https://github.com/facebookresearch/Replica-Dataset).


## Usage

### Main

```shell
  $ roslaunch habitat_ros single_robot_bringup.launch # single robot
  $ roslaunch habitat_ros dual_robot_bringup.launch # dual robots (in a new terminal) 
  $ cd scripts/ && python3 capture.py --robot_name <your robot name> # capture rgd & semantic images to build your own dataset
```
This launch file starts the `habitat_mav_sim_node` and `habitat_node`, you can modify the parameters in config/habitat(_mav_sim).yaml to load your own scene and change the settings.

#### Published topics

This node publishes the ground truth pose, RGB, depth, tf and optionally semantics at a constant rate configurable from `fps`.

| Topic name                               | Type                          | Description |
| :--------------------------------------- | :---------------------------- | :---------- |
| `/${robot_name}/pose`                          | `geometry_msgs::PoseStamped`  | The pose (T\_PB) where the images are rendered from. |
| `/${robot_name}/depth/image_raw`               | `sensor_msgs::Image (32FC1)`  | The rendered depth image in metres. |
| `/${robot_name}/rgb/image_raw`                 | `sensor_msgs::Image (rgb8)`   | The rendered RGB image. |
| `/${robot_name}/semantic_class/image_raw`      | `sensor_msgs::Image (mono8)`  | The per-pixel semantic class IDs. Each class ID is in the range [0-41]. Published only if `enable_semantics` is `true`. |
| `/${robot_name}/semantic_instance/image_raw`   | `sensor_msgs::Image (mono16)` | The per-pixel semantic instance IDs. Published only if `enable_semantics` is `true`. |
| `/${robot_name}/semantic_class/image_color`    | `sensor_msgs::Image (rgb8)`   | A color render of the semantic class ID image. Useful for visualization and debugging. Published only if `visualize_semantics` is `true`. |
| `/${robot_name}/semantic_instance/image_color` | `sensor_msgs::Image (rgb8)`   | A color render of the semantic instance ID image. Useful for visualization and debugging. Published only if `visualize_semantics` is `true`. |

#### Subscribed topics

The node subscribes to a single topic which is used to set the pose the images
are rendered from. Once a new pose is received, the Habitat-Sim camera is
immediately moved there.

| Topic name               | Type                         | Description |
| :----------------------- | :--------------------------- | :---------- |
| `/${robot_name}/external_pose` | `geometry_msgs::PoseStamped` | The pose (T\_EB) where the next images should be rendered from. |

#### Settings

| Setting name                         | Type    | Description |
| :----------------------------------- | :------ | :---------- |
| `width`                      | `int`   | The width of all rendered images in pixels. |
| `height`                     | `int`   | The height of all rendered images in pixels. |
| `near_plane`                 | `float` | The near plane of the depth sensor in metres. No depth values smaller than `near_plane` will be produced. |
| `far_plane`                  | `float` | The far plane of the depth sensor in metres. No depth values greater than `far_plane` will be produced. |
| `f`                          | `float` | The focal length of the sensors in pixels. Habitat-Sim doesn't currently support different focal lengths between the x and y axes. |
| `fps`                        | `float` | The rate at which the ground truth pose and rendered images are published in Hz. Set to 0 to publish as fast as possible. |
| `enable_semantics`           | `bool`  | Enable publishing of the semantic class and instance IDs. |
| `depth_noise`                | `bool`  | Enable [Redwood depth noise](http://redwood-data.org/indoor/dataset.html). |
| `allowed_classes`            | `List`  | Only class IDs present in this list will be present in the output images. All other object classes will have a class and instance ID of 0. Leave empty to return all the available classes. Having a non-empty list significantly impacts performance so its suggested to only use this option for debugging. |
| `scene_file`                 | `str`   | The path to the .glb scene file to load. The path can be absolute, relative to the habitat\_ros package or it may start with `~` to indicate the home directory of the current user. |
| `initial_T_HB`               | `List`  | The initial body pose. Can be a translation only `[tx, ty, tz]`, rotation only `[qx, qy, qz, qw]`, translation and rotation `[tx, ty, tz, qx, qy, qz, qw]` or the 16 elements of a homogeneous transformation matrix in row-major order. |
| `pose_frame_at_initial_T_HB` | `bool`  | Enable publishing a static transform so that the Pose frame (P) coincides with the initial T\_HB pose. This results in the initial published pose being the identity matrix. |
| `world_frame_id`              | `str`   | The ID of the frame for poses published in `/${robot_name}/pose`. |
| `base_frame_id` | `str`  | The ID of the robot base frame |
| `camera_frame_id` | `str`  | The ID of the camera frame |
| `visualize_semantics`        | `bool`  | Generate and publish visualizations of the semantic class and instance IDs. Useful for debugging. |
| `recording_dir`              | `srt`   | Store the run as a dataset in the TUM RGB-D format in `recording_dir`. |


## Performance

- Enabling the semantic class and instance publishing will reduce performance so it is advised to keep them disabled if semantics are not needed.
- Enabling semantic class and instance visualization publishing will reduce performance even more so it is advised to keep them disabled if not needed.



## Acknowledgments

This code is based on the work from [Smart Robotics Lab's habitat-ros repository](https://github.com/smartroboticslab/habitat-ros.git). Thanks to the authors for their contribution.


