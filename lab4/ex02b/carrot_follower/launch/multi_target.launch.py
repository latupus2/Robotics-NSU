from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    package_name = 'carrot_follower'
    pkg_share = get_package_share_directory(package_name)
    rviz_config_path = os.path.join(pkg_share, 'config', 'carrot.rviz')
    
    radius = LaunchConfiguration('radius')
    direction = LaunchConfiguration('direction_of_rotation')
    switch_threshold = LaunchConfiguration('switch_threshold')

    return LaunchDescription([
        DeclareLaunchArgument('radius', default_value='2.0', description='Radius for carrot rotation'),
        DeclareLaunchArgument('direction_of_rotation', default_value='1', description='1 for clockwise, -1 for counterclockwise'),
        DeclareLaunchArgument('switch_threshold', default_value='1.0', description='Distance threshold for auto target switching'),

        # Turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),

        # Spawn turtle2 with delay
        TimerAction(
            period=2.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn', 
                         '{x: 3.0, y: 3.0, theta: 0.0, name: "turtle2"}'],
                    output='screen'
                )
            ]
        ),

        # Spawn turtle3 with delay
        TimerAction(
            period=3.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn', 
                         '{x: 5.0, y: 5.0, theta: 0.0, name: "turtle3"}'],
                    output='screen'
                )
            ]
        ),

        # Turtle1 TF broadcaster
        Node(
            package='carrot_follower',
            executable='turtle_tf2_broadcaster',
            name='broadcaster1',
            parameters=[{'turtlename': 'turtle1'}]
        ),

        # Turtle2 TF broadcaster
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='carrot_follower',
                    executable='turtle_tf2_broadcaster',
                    name='broadcaster2',
                    parameters=[{'turtlename': 'turtle2'}]
                )
            ]
        ),

        # Turtle3 TF broadcaster
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='carrot_follower',
                    executable='turtle_tf2_broadcaster',
                    name='broadcaster3',
                    parameters=[{'turtlename': 'turtle3'}]
                )
            ]
        ),

        # Target switcher node
        TimerAction(
            period=6.0,
            actions=[
                Node(
                    package='carrot_follower',
                    executable='target_switcher',
                    name='target_switcher',
                    parameters=[
                        {'radius': radius},
                        {'direction_of_rotation': direction},
                        {'switch_threshold': switch_threshold}
                    ]
                )
            ]
        ),


        # RViz2
        TimerAction(
            period=7.0,
            actions=[
                Node(
                    package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    arguments=['-d', rviz_config_path],
                    output='screen'
                )
            ]
        ),
    ])