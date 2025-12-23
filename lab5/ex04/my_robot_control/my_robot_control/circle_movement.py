#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CircleMovement(Node):
    def __init__(self):
        super().__init__('circle_movement')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.1  # 10 Hz
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('Circle movement node started, publishing to /cmd_vel')

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.5  # Линейная скорость (m/s)
        msg.angular.z = 0.5  # Угловая скорость (rad/s) для круга
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CircleMovement()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()