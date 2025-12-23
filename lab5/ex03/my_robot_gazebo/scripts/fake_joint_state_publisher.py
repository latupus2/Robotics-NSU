#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
import math

class FakeJointStatePublisher(Node):
    def __init__(self):
        super().__init__('fake_joint_state_publisher')
        
        # Публикатор для joint states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Подписчик на odom для вычисления положения колес
        self.odom_sub = self.create_subscription(
            Odometry, 
            '/odom', 
            self.odom_callback, 
            10
        )
        
        self.get_logger().info('Fake Joint State Publisher Started')
        
        # Переменные для хранения положения колес
        self.left_wheel_pos = 0.0
        self.right_wheel_pos = 0.0
        self.last_time = self.get_clock().now()
        
    def odom_callback(self, msg):
        # Вычисляем скорость колес на основе odometry
        # Это упрощенная модель - в реальности нужно учитывать кинематику
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        
        if dt > 0:
            # Линейная и угловая скорости из odom
            linear_vel = msg.twist.twist.linear.x
            angular_vel = msg.twist.twist.angular.z
            
            # Кинематика дифференциального привода
            wheel_separation = 1.1
            wheel_radius = 0.15
            
            left_wheel_vel = (linear_vel - angular_vel * wheel_separation / 2) / wheel_radius
            right_wheel_vel = (linear_vel + angular_vel * wheel_separation / 2) / wheel_radius
            
            # Интегрируем скорость для получения положения
            self.left_wheel_pos += left_wheel_vel * dt
            self.right_wheel_pos += right_wheel_vel * dt
            
            # Публикуем joint states
            self.publish_joint_states()
            
            self.last_time = current_time
        
    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        msg.name = ['left_wheel_joint', 'right_wheel_joint']
        msg.position = [self.left_wheel_pos, self.right_wheel_pos]
        msg.velocity = [0.0, 0.0]  # Можно вычислить реальную скорость
        msg.effort = []
        
        self.joint_pub.publish(msg)

def main():
    rclpy.init()
    node = FakeJointStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()