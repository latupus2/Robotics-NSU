from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    package_name = 'time_delay_follower'
    pkg_share = get_package_share_directory(package_name)
    rviz_config_path = os.path.join(pkg_share, 'config', 'carrot.rviz')
    
    delay = LaunchConfiguration('delay')
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'delay',
            default_value='5.0',
            description='Time delay in seconds for turtle2 to follow turtle1'
        ),
        
        # Turtlesim node
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim',
            output='screen'
        ),
        
        # Spawn turtle2 after delay
        TimerAction(
            period=2.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn',
                        '{x: 3.0, y: 3.0, theta: 0.0, name: "turtle2"}'
                    ],
                    output='screen'
                )
            ]
        ),
        
        # TF broadcaster for turtle1
        Node(
            package='time_delay_follower',
            executable='turtle_tf2_broadcaster',
            name='broadcaster1',
            parameters=[{'turtle_name': 'turtle1'}],
            output='screen'
        ),
        
        # TF broadcaster for turtle2 (with delay to ensure turtle2 exists)
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='time_delay_follower',
                    executable='turtle_tf2_broadcaster',
                    name='broadcaster2',
                    parameters=[{'turtle_name': 'turtle2'}],
                    output='screen'
                )
            ]
        ),
        
        # Time delayed follower node
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='time_delay_follower',
                    executable='turtle_tf2_time_delayed_listener',
                    name='listener',
                    parameters=[{'delay': delay}],
                    output='screen'
                )
            ]
        ),
        
        # RViz2 with configuration
        TimerAction(
            period=5.0,
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