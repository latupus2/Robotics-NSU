#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import cv2
from cv_bridge import CvBridge
import numpy as np

class DepthCameraStopper(Node):
    def __init__(self):
        super().__init__('depth_camera_stopper')
        
        self.stop_distance = 1.5  
        self.linear_speed = 0.3   
        
        self.bridge = CvBridge()
        self.obstacle_detected = False
        
        self.depth_sub = self.create_subscription(
            Image,
            '/model/my_robot/depth_camera/image',
            self.depth_callback,
            10
        )
        
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        self.get_logger().info('Depth Camera Stopper запущен')
    
    def depth_callback(self, msg):
        try:
            
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
            
            height, width = depth_image.shape
            
            roi_height = 80
            roi_width = 100
            y_start = height // 2 - roi_height // 2
            y_end = height // 2 + roi_height // 2
            x_start = width // 2 - roi_width // 2
            x_end = width // 2 + roi_width // 2
            
            roi = depth_image[y_start:y_end, x_start:x_end]
            
            roi_valid = roi[(roi > 0) & (roi < 100)]
            
            if roi_valid.size > 0:
                
                min_dist = np.min(roi_valid)
                
                
                self.obstacle_detected = min_dist < self.stop_distance
                
                cmd_vel = Twist()
                
                if self.obstacle_detected:
                    cmd_vel.linear.x = 0.0
                    self.get_logger().info(f'СТОП! Препятствие на {min_dist:.2f} м')
                else:
                    cmd_vel.linear.x = self.linear_speed
                    self.get_logger().info(f'ВПЕРЕД. Расстояние: {min_dist:.2f} м')
                
                cmd_vel.angular.z = 0.0
                self.cmd_vel_pub.publish(cmd_vel)
                
        except Exception as e:
            self.get_logger().error(f'Ошибка обработки изображения: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = DepthCameraStopper()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop_msg = Twist()
        node.cmd_vel_pub.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()