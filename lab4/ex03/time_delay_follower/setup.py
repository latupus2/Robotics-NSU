from setuptools import find_packages, setup

package_name = 'time_delay_follower'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/time_delay_follow.launch.py']),
        ('share/' + package_name + '/config', ['config/carrot.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='latup',
    maintainer_email='latup@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtle_tf2_broadcaster = time_delay_follower.turtle_tf2_broadcaster:main',
            'turtle_tf2_time_delayed_listener = time_delay_follower.turtle_tf2_time_delayed_listener:main',
        ],
    },
)
