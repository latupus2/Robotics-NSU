#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_gazebo = get_package_share_directory('my_unique_robot_gazebo')

    # Xacro → URDF
    xacro_file = os.path.join(pkg_gazebo, 'config', 'robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    world_path = os.path.join(pkg_gazebo, 'config', 'simple_lidar.sdf')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': f'-r --render-engine ogre2 -v 4 {world_path}'
        }.items(),
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
            'publish_frequency': 50.0,
            'joint_state_topic': '/joint_states'
        }],
        output='screen'
    )

    # Bridge (полная версия как в robot_lidar.launch.py)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/model/my_robot/lidar/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
        ],
        output='screen'
    )

    # Static TF для колёс (как в robot_lidar.launch.py)
    static_transform_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0.55', '0', '0', '0', '0', 'base_link', 'left_wheel'],
        name='left_wheel_tf_publisher',
        output='screen'
    )

    static_transform_publisher2 = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '-0.55', '0', '0', '0', '0', 'base_link', 'right_wheel'],
        name='right_wheel_tf_publisher',
        output='screen'
    )

    # RViz с конфигом
    rviz_config = os.path.join(pkg_gazebo, 'config', 'rviz_config_lidar.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Odom to TF broadcaster
    odom_tf_publisher = Node(
        package='my_unique_robot_gazebo',
        executable='odom_to_tf.py',
        name='odom_to_tf_publisher',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Узел остановки перед препятствием
    obstacle_stop_node = Node(
        package='my_unique_robot_gazebo',
        executable='obstacle_stop_node.py',
        name='obstacle_stop_node',
        parameters=[{
            'min_safe_distance': 2.0,   # Останавливаться за 2 метра до препятствия
            'forward_speed': 0.5,       # Скорость движения вперед
            'angle_range': 60.0,        # Анализировать ±30 градусов
            'scan_topic': '/model/my_robot/lidar/scan',
            'cmd_vel_topic': '/cmd_vel',
            'control_frequency': 20.0   # Частота управления 20 Гц
        }],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_robot,
        robot_state_publisher,
        static_transform_publisher,
        static_transform_publisher2,
        bridge,
        rviz,
        odom_tf_publisher,
        obstacle_stop_node
    ])