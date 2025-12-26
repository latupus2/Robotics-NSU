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

    # Gazebo с миром simple_lidar.sdf
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': '-r --render-engine ogre2 -v 4 ' + os.path.join(pkg_gazebo, 'config', 'simple_lidar.sdf')
        }.items(),
    )

    # Spawn робота
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot', '-z', '0.01'],
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

    # Bridge с добавлением камеры глубины
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/model/my_robot/lidar/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/model/my_robot/depth_camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/model/my_robot/depth_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo'
        ],
        output='screen'
    )

    # Static TF для колёс
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

    # RViz без конфига
    rviz = Node(
        package='rviz2',
        executable='rviz2',
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

    # Static TF для лидара
    lidar_tf_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0.7', '0', '0', '0', 'base_link', 'lidar_link'],
        name='lidar_tf_publisher',
        output='screen'
    )

    # Static TF для камеры глубины
    # depth_camera_tf_publisher = Node(
    #     package='tf2_ros',
    #     executable='static_transform_publisher',
    #     arguments=['-0.15', '0', '0.1', '0', '0', '0', 'upper_body', 'depth_camera_link'],
    #     name='depth_camera_tf_publisher',
    #     output='screen'
    # )

    return LaunchDescription([
        gazebo,
        spawn_robot,
        robot_state_publisher,
        static_transform_publisher,
        static_transform_publisher2,
        lidar_tf_publisher,
        # depth_camera_tf_publisher,
        bridge,
        rviz,
        odom_tf_publisher
    ])