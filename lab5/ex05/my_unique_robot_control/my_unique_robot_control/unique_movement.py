#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class ZigzagMovement(Node):
    def __init__(self):
        super().__init__('zigzag_movement')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.phase = 0  # 0: Назад+влево, 1: Вперёд+вправо
        self.counter = 0
        self.get_logger().info('Zigzag movement started (back-left / forward-right)')

    def timer_callback(self):
        msg = Twist()
        self.counter += 1
        
        if self.phase == 0:  # Фаза 1: НАЗАД и ВЛЕВО
            msg.linear.x = -0.5    # Отрицательное = назад
            msg.angular.z = 0.5    # Положительное = поворот влево (против часовой)
            if self.counter > 60:  # ~6 секунд (60 * 0.1)
                self.phase = 1
                self.counter = 0
                self.get_logger().info('Switching to: FORWARD + RIGHT')
                
        elif self.phase == 1:  # Фаза 2: ВПЕРЁД и ВПРАВО
            msg.linear.x = 0.5     # Положительное = вперёд
            msg.angular.z = -0.5   # Отрицательное = поворот вправо (по часовой)
            if self.counter > 60:  # ~6 секунд
                self.phase = 0
                self.counter = 0
                self.get_logger().info('Switching to: BACK + LEFT')
        
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ZigzagMovement()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()