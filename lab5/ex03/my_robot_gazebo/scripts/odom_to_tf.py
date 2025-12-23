#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
import tf2_ros
import math

class OdomToTf(Node):
    def __init__(self):
        super().__init__('odom_to_tf')
        
        # Broadcaster для трансформаций
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        
        # Подписчик на odom
        self.odom_sub = self.create_subscription(
            Odometry, 
            '/odom', 
            self.odom_callback, 
            10
        )
        
        self.get_logger().info('Odom to TF Bridge Started')
        
    def odom_callback(self, msg):
        # Создаем трансформацию из odom в base_link
        transform = TransformStamped()
        
        # Временная метка и фреймы
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'odom'  # родительский фрейм
        transform.child_frame_id = 'base_link'  # дочерний фрейм
        
        # Позиция из odometry
        transform.transform.translation.x = msg.pose.pose.position.x
        transform.transform.translation.y = msg.pose.pose.position.y
        transform.transform.translation.z = msg.pose.pose.position.z
        
        # Ориентация из odometry
        transform.transform.rotation.x = msg.pose.pose.orientation.x
        transform.transform.rotation.y = msg.pose.pose.orientation.y
        transform.transform.rotation.z = msg.pose.pose.orientation.z
        transform.transform.rotation.w = msg.pose.pose.orientation.w
        
        # Публикуем трансформацию
        self.tf_broadcaster.sendTransform(transform)

def main():
    rclpy.init()
    node = OdomToTf()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()