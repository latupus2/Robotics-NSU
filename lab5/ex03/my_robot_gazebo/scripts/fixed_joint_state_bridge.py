#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
import math

class FixedJointStateBridge(Node):
    def __init__(self):
        super().__init__('fixed_joint_state_bridge')
        
        # Публикатор для joint states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Подписчик на odom
        self.odom_sub = self.create_subscription(
            Odometry, 
            '/odom', 
            self.odom_callback, 
            10
        )
        
        self.get_logger().info('Fixed Joint State Bridge Started')
        
        # Переменные для хранения положения колес
        self.left_wheel_pos = 0.0
        self.right_wheel_pos = 0.0
        self.last_time = None
        self.last_linear_vel = 0.0
        self.last_angular_vel = 0.0
        
        # Параметры робота
        self.wheel_radius = 0.15
        self.wheel_separation = 1.1
        
    def odom_callback(self, msg):
        current_time = self.get_clock().now()
        
        if self.last_time is None:
            self.last_time = current_time
            return
            
        # Вычисляем dt
        dt = (current_time - self.last_time).nanoseconds / 1e9
        
        if dt <= 0:
            return
            
        # Получаем скорости из odom
        linear_vel = msg.twist.twist.linear.x
        angular_vel = msg.twist.twist.angular.z
        
        # Вычисляем скорости колес по кинематике дифференциального привода
        left_wheel_vel = (linear_vel - angular_vel * self.wheel_separation / 2) / self.wheel_radius
        right_wheel_vel = (linear_vel + angular_vel * self.wheel_separation / 2) / self.wheel_radius
        
        # Интегрируем для получения положения
        self.left_wheel_pos += left_wheel_vel * dt
        self.right_wheel_pos += right_wheel_vel * dt
        
        # Публикуем joint states
        joint_msg = JointState()
        joint_msg.header.stamp = current_time.to_msg()
        joint_msg.header.frame_id = 'base_link'
        joint_msg.name = ['left_wheel_joint', 'right_wheel_joint']
        joint_msg.position = [self.left_wheel_pos, self.right_wheel_pos]
        joint_msg.velocity = [left_wheel_vel, right_wheel_vel]
        joint_msg.effort = []
        
        self.joint_pub.publish(joint_msg)
        
        # Логируем для отладки (можно убрать позже)
        self.get_logger().info(f'Positions: left={self.left_wheel_pos:.3f}, right={self.right_wheel_pos:.3f}, linear_vel={linear_vel:.3f}')
        
        self.last_time = current_time
        self.last_linear_vel = linear_vel
        self.last_angular_vel = angular_vel

def main():
    rclpy.init()
    node = FixedJointStateBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()