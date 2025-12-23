#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class UniqueMovement(Node):
    def __init__(self):
        super().__init__('unique_movement')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.phase = 0  # 0: Прямо + правый поворот, 1: Прямо + левый поворот
        self.counter = 0
        self.get_logger().info('Unique movement (figure-8) started')

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.5  # Постоянная линейная скорость
        self.counter += 1
        if self.phase == 0:  # Правый круг
            msg.angular.z = 0.5
            if self.counter > 60:  # ~6 сек
                self.phase = 1
                self.counter = 0
        elif self.phase == 1:  # Левый круг
            msg.angular.z = -0.5
            if self.counter > 60:
                self.phase = 0
                self.counter = 0
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = UniqueMovement()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()