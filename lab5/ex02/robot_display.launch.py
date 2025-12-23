#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import subprocess

def generate_launch_description():
    package_dir = get_package_share_directory('my_robot_description')
    
    # Убедитесь, что путь правильный - возможно у вас 'urdf' вместо 'ex01'
    xacro_path = os.path.join(package_dir, 'urdf', 'robot.urdf.xacro')
    
    print(f"Looking for xacro at: {xacro_path}")  # Для отладки
    
    # Проверяем существование файла
    if not os.path.exists(xacro_path):
        raise FileNotFoundError(f"Xacro file not found at: {xacro_path}")
    
    # Обрабатываем xacro через командную строку
    try:
        robot_description = subprocess.check_output(
            ['xacro', xacro_path], 
            text=True
        )
        print("Xacro processed successfully!")  # Для отладки
    except Exception as e:
        print(f"Error processing xacro: {e}")
        raise

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', os.path.join(package_dir, 'rviz', 'lab5ex12.rviz')],
        ),
    ])