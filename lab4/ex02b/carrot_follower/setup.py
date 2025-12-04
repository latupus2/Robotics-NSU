from setuptools import setup

package_name = 'carrot_follower'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/turtles_tf2.launch.py']),
        ('share/' + package_name + '/launch', ['launch/multi_target.launch.py']),
        ('share/' + package_name + '/config', ['config/carrot.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='TF2 carrot follower package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtle_tf2_broadcaster = carrot_follower.turtle_tf2_broadcaster:main',
            'turtle_tf2_listener = carrot_follower.turtle_tf2_listener:main',
            'carrot_tf2_broadcaster = carrot_follower.carrot_tf2_broadcaster:main',
            'target_switcher = carrot_follower.target_switcher:main',
            'turtle_controller = carrot_follower.turtle_controller:main',
        ],
    },
)