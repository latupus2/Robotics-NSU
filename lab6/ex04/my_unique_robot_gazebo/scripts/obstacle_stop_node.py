#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math

class ObstacleStopNode(Node):
    def __init__(self):
        super().__init__('obstacle_stop_node')
        
        # Параметры
        self.declare_parameter('min_safe_distance', 2.0)
        self.declare_parameter('forward_speed', 0.5)
        self.declare_parameter('scan_topic', '/model/my_robot/lidar/scan')
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('angle_range', 60.0)
        self.declare_parameter('debug', True)
        self.declare_parameter('control_frequency', 20.0)  # Hz
        
        self.min_safe_distance = self.get_parameter('min_safe_distance').value
        self.forward_speed = self.get_parameter('forward_speed').value
        self.scan_topic = self.get_parameter('scan_topic').value
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.angle_range = math.radians(self.get_parameter('angle_range').value / 2)
        self.debug = self.get_parameter('debug').value
        self.control_frequency = self.get_parameter('control_frequency').value
        
        self.scan_sub = self.create_subscription(
            LaserScan,
            self.scan_topic,
            self.scan_callback,
            10
        )
        
        self.cmd_vel_pub = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        
        self.obstacle_detected = False
        self.last_min_distance = float('inf')
        self.scan_count = 0
        self.control_count = 0
        
        self.get_logger().info(f'=== OBSTACLE STOP NODE STARTED ===')
        self.get_logger().info(f'Min safe distance: {self.min_safe_distance} m')
        self.get_logger().info(f'Forward speed: {self.forward_speed} m/s')
        self.get_logger().info(f'Control frequency: {self.control_frequency} Hz')
        self.get_logger().info(f'Analyzing angle range: ±{self.get_parameter("angle_range").value/2}°')
        
        timer_period = 1.0 / self.control_frequency
        self.timer = self.create_timer(timer_period, self.control_loop)
        
    def scan_callback(self, msg):
        """Обработка данных с лидара"""
        self.scan_count += 1
        
        if len(msg.ranges) == 0:
            self.get_logger().warn('No laser scan data received!')
            return
            
        angle_min = msg.angle_min
        angle_increment = msg.angle_increment
        min_distance = float('inf')
        min_angle = 0.0
        
        valid_points = 0
        for i, distance in enumerate(msg.ranges):
            if (distance == float('inf') or distance == float('-inf') or 
                distance == 0.0 or distance > 100.0):
                continue
                
            angle = angle_min + i * angle_increment
            
            if abs(angle) <= self.angle_range:
                valid_points += 1
                if distance < min_distance:
                    min_distance = distance
                    min_angle = angle
        
        if min_distance < float('inf'):
            self.last_min_distance = min_distance
            if self.scan_count % 20 == 0 and self.debug:
                self.get_logger().info(f'[LIDAR] Front sector: {valid_points} points, min={min_distance:.2f}m at angle={math.degrees(min_angle):.1f}°')
        else:
            self.last_min_distance = 100.0  
            if self.scan_count % 20 == 0 and self.debug:
                self.get_logger().info(f'[LIDAR] Front sector: {valid_points} points, NO OBSTACLES')
        
        self.obstacle_detected = (self.last_min_distance < self.min_safe_distance)
        
        if self.obstacle_detected and min_distance < self.min_safe_distance * 1.1:
            self.get_logger().warn(f'⚠️  OBSTACLE DETECTED at {self.last_min_distance:.2f} m!')
    
    def control_loop(self):
        
        self.control_count += 1
        
        cmd_vel = Twist()
        
        if not self.obstacle_detected:
            # Путь свободен
            cmd_vel.linear.x = self.forward_speed
            cmd_vel.angular.z = 0.0
            status = "▶️  MOVING FORWARD"
        else:
            # Препятствие обнаружено 
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0
            status = "⛔ STOPPED - OBSTACLE AHEAD"
        
        self.cmd_vel_pub.publish(cmd_vel)
        
        # Логируем состояние раз в 10 циклов 
        if self.control_count % 20 == 0:
            if self.last_min_distance < float('inf'):
                self.get_logger().info(f'[CONTROL] {status}, Distance: {self.last_min_distance:.2f} m, Speed: {cmd_vel.linear.x:.1f} m/s')
            else:
                self.get_logger().info(f'[CONTROL] {status}, Speed: {cmd_vel.linear.x:.1f} m/s')

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleStopNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt received')
    finally:
        # Останавливаем робота при завершении
        stop_cmd = Twist()
        node.cmd_vel_pub.publish(stop_cmd)
        node.get_logger().info('=== NODE STOPPED ===')
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()