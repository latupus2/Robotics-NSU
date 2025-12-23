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
    pkg_description = get_package_share_directory('my_robot_description')

    # Xacro → URDF
    xacro_file = os.path.join(pkg_gazebo, 'ex05', 'robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': '-r --render-engine ogre -v 4 ' + os.path.join(pkg_gazebo, 'ex05', 'world.sdf')
        }.items(),
    )

    # Spawn
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot', '-z', '0.01'],
        output='screen'
    )

    # Robot state publisher (remap joint_states)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
            'publish_frequency': 50.0,
            'joint_state_topic': '/joint_states'  # Убедитесь, что совпадает с плагином
        }],
        output='screen'
    )

    # Bridge (замените gz.msgs на ignition.msgs, добавьте /tf и /joint_states)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',  # ROS → GZ
            '/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry',    # GZ → ROS
            '/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model',  # Измените на /joint_states
            '/tf@tf2_msgs/msg/TFMessage@ignition.msgs.Pose_V'        # Добавьте: Bridge для TF
        ],
        output='screen'
    )

    # Static TF (без изменений)
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

    # RViz (без изменений)
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_description, 'ex02', 'default.rviz')],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

# Odom to TF broadcaster (workaround для Fortress)
    odom_tf_publisher = Node(
        package='my_robot_gazebo',
        executable='odom_to_tf.py',
        name='odom_to_tf_publisher',
        parameters=[{'use_sim_time': True}],
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
        odom_tf_publisher
    ])