"""
A launch file for running the motion planning python api tutorial
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    # Define your package variables clearly
    moveit_pkg = "antonie_moveit_config"
    scripts_pkg = "my_manipulator"

    # Use the official MoveItConfigsBuilder pattern mapped to your packages
    moveit_config = (
        MoveItConfigsBuilder(
            robot_name="antonie", package_name=moveit_pkg
        )
        # Point to your exact Xacro configuration file name
        .robot_description(file_path="config/antonie_new.urdf.xacro")
        # Point to your controller setups
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        # Pull your application-level moveit_py configurations
        .moveit_cpp(
            file_path=os.path.join(
                get_package_share_directory(scripts_pkg), "config", "moveit_py.yaml"
            )
        )
        .to_moveit_configs()
    )

    script_file = DeclareLaunchArgument(
        "script_file",
        default_value="moveit_py_example_node",
        description="Python API script file name",
    )

    # Convert configs to parameter dictionary and inject sim time
    parameters = moveit_config.to_dict()
    parameters['use_sim_time'] = True

    moveit_py_node = Node(
        name="moveit_py_example_node", # Keeps node name synchronized with script
        package=scripts_pkg,
        executable=LaunchConfiguration("script_file"),
        output="both",
        parameters=[parameters],
    )

    return LaunchDescription(
        [
            script_file,
            moveit_py_node,
        ]
    )
