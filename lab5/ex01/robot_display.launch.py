#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import launch_ros


def generate_launch_description():
    # Путь к URDF-файлу
    package_dir = get_package_share_directory('my_robot_description')
    urdf_path = os.path.join(package_dir, 'ex01', 'robot.urdf')

    # Читаем URDF как строку
    with open(urdf_path, 'r') as infp:
        robot_description_content = infp.read()

    return LaunchDescription([
        # Публикуем описание робота
       Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description_content,
                'use_sim_time': False,           # ← добавь
            }],
            remappings=[('/robot_description', '/robot_description')],  # ← добавь эту строку
        ),

        # GUI для управления суставами
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            #arguments=['-d', os.path.join(package_dir, 'ex01', 'default.rviz')],
            # Если файла default.rviz нет — просто закомментируй строку arguments выше
        ),
    ])