#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo = get_package_share_directory('my_robot_gazebo')

    # Include предыдущий launch для Gazebo и RViz
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'ex03', 'robot_gazebo.launch.py')
        )
    )

    # Узел для circle movement
    circle_node = Node(
        package='my_robot_control',
        executable='circle_movement',
        name='circle_movement',
        output='screen'
    )

    return LaunchDescription([
        gazebo_launch,
        circle_node
    ])