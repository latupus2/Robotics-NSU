#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_gazebo = get_package_share_directory('my_unique_robot_gazebo')
    
    # Xacro → URDF
    xacro_file = os.path.join(pkg_gazebo, 'config', 'robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()
    
    # Запуск Gazebo с миром
    world_path = os.path.join(pkg_gazebo, 'config', 'ex04_simple_world.sdf')
    
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-v', '4', world_path],
        output='screen'
    )
    
    # Spawn робота
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot', '-z', '0.5'],
        output='screen'
    )
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
        output='screen'
    )
    
    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/model/my_robot/lidar/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
        ],
        output='screen'
    )
    
    # Узел остановки перед препятствием
    obstacle_stop_node = Node(
        package='my_unique_robot_gazebo',
        executable='obstacle_stop_node.py',
        name='obstacle_stop_node',
        parameters=[{
            'min_safe_distance': 1.5,
            'forward_speed': 0.3,
        }],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot,
        bridge,
        obstacle_stop_node,
    ])