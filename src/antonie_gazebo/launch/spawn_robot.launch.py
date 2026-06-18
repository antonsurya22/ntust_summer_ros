import os
import xacro
import yaml
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None

def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except EnvironmentError:
        return None

def generate_launch_description():
    moveit_pkg = "antonie_moveit_config"
    gazebo_pkg = "antonie_gazebo"

    # 1. Parse the URDF description via xacro
    urdf_path = os.path.join(get_package_share_directory(moveit_pkg), "config", "antonie_new.urdf.xacro")
    robot_description_config = xacro.process_file(urdf_path)
    robot_description = {"robot_description": robot_description_config.toxml()}

    # 2. Parse Semantic Description (SRDF) - THIS FIXES THE RVIZ EMPTY DOCUMENT ERROR
    robot_description_semantic = {"robot_description_semantic": load_file(moveit_pkg, "config/antonie.srdf")}

    # 3. Load supplementary Kinematics configurations
    kinematics_yaml = load_yaml(moveit_pkg, "config/kinematics.yaml")
    joint_limits_yaml = load_yaml(moveit_pkg, "config/joint_limits.yaml")

    # Combine configurations together to pass into RViz and MoveGroup
    moveit_base_params = [
        robot_description,
        robot_description_semantic,
        kinematics_yaml,
        joint_limits_yaml,
        {"use_sim_time": True}
    ]

    # Node A: Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": True}]
    )

    # Node B: Gazebo Model Spawner Injection Entity
    gz_spawn_model = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "/robot_description", "-name", "antonie", "-allow_renaming", "false"],
        parameters=[{"use_sim_time": True}]
    )

    # Controller Spawners
    jsb_spawner = Node(
        package="controller_manager", executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "/controller_manager"], output="screen"
    )
    arm_spawner = Node(
        package="controller_manager", executable="spawner",
        arguments=["arm_controller", "-c", "/controller_manager"], output="screen"
    )
    gripper_spawner = Node(
        package="controller_manager", executable="spawner",
        arguments=["gripper_controller", "-c", "/controller_manager"], output="screen"
    )

    # Node C: Include MoveIt background context script cleanly
    move_group_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(moveit_pkg), "launch", "move_group.launch.py")
        ),
        launch_arguments={"use_sim_time": "true"}.items()
    )

    # Node D: Explicit RViz execution container loaded with all the required semantic variables
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", os.path.join(get_package_share_directory(moveit_pkg), "config", "moveit.rviz")],
        parameters=moveit_base_params # Forces RViz to see your planning groups instantly!
    )

    return LaunchDescription([
        robot_state_publisher,
        gz_spawn_model,
        jsb_spawner,
        arm_spawner,
        gripper_spawner,
        move_group_include,
        rviz_node
    ])
