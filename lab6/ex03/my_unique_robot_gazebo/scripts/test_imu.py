#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class TestImu(Node):
    def __init__(self):
        super().__init__('test_imu')
        self.subscription = self.create_subscription(
            Imu,
            '/model/my_robot/imu',
            self.imu_callback,
            10
        )
        self.get_logger().info('Test IMU node started')

    def imu_callback(self, msg):
        self.get_logger().info(
            f'IMU Data:\n'
            f'  Orientation: [{msg.orientation.x:.3f}, {msg.orientation.y:.3f}, {msg.orientation.z:.3f}, {msg.orientation.w:.3f}]\n'
            f'  Angular Vel: [{msg.angular_velocity.x:.3f}, {msg.angular_velocity.y:.3f}, {msg.angular_velocity.z:.3f}]\n'
            f'  Linear Accel: [{msg.linear_acceleration.x:.3f}, {msg.linear_acceleration.y:.3f}, {msg.linear_acceleration.z:.3f}]'
        )

def main(args=None):
    rclpy.init(args=args)
    node = TestImu()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()