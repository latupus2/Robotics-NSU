#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class MoveToGoal(Node):
    def __init__(self):
        super().__init__('move_to_goal')
        # Объявляем параметры x, y, theta
        self.declare_parameter('x', 0.0)
        self.declare_parameter('y', 0.0)
        self.declare_parameter('theta', 0.0)
        
        # Получаем параметры
        self.goal_x = self.get_parameter('x').get_parameter_value().double_value
        self.goal_y = self.get_parameter('y').get_parameter_value().double_value
        self.goal_theta = self.get_parameter('theta').get_parameter_value().double_value
        
        # Подписка и публикация
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Текущая позиция
        self.current_pose = Pose()
        # ПИД-константы
        self.linear_kp = 1.0
        self.angular_kp = 2.0
        self.tolerance = 0.1
        self.angular_tolerance = 0.05
        # Флаг достижения цели
        self.goal_reached = False

    def pose_callback(self, msg):
        self.current_pose = msg
        if not self.goal_reached:
            self.move_to_goal()

    def move_to_goal(self):
        cmd = Twist()
        
        # Вычисляем расстояние до цели
        dx = self.goal_x - self.current_pose.x
        dy = self.goal_y - self.current_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Вычисляем угол до цели
        angle_to_goal = math.atan2(dy, dx)
        angle_error = angle_to_goal - self.current_pose.theta
        
        # Нормализация угла
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi
        
        # Линейная скорость
        if distance > self.tolerance:
            cmd.linear.x = self.linear_kp * distance
            cmd.linear.x = min(max(cmd.linear.x, -2.0), 2.0)
        else:
            cmd.linear.x = 0.0
        
        # Угловая скорость
        if abs(angle_error) > self.angular_tolerance:
            cmd.angular.z = self.angular_kp * angle_error
            cmd.angular.z = min(max(cmd.angular.z, -4.0), 4.0)
        else:
            cmd.angular.z = 0.0
        
        # Коррекция ориентации, если позиция достигнута
        if distance <= self.tolerance:
            angle_error = self.goal_theta - self.current_pose.theta
            while angle_error > math.pi:
                angle_error -= 2 * math.pi
            while angle_error < -math.pi:
                angle_error += 2 * math.pi
            if abs(angle_error) > self.angular_tolerance:
                cmd.angular.z = self.angular_kp * angle_error
                cmd.angular.z = min(max(cmd.angular.z, -4.0), 4.0)
            else:
                cmd.angular.z = 0.0
                self.goal_reached = True
                self.get_logger().info(f'Goal reached: x={self.current_pose.x:.2f}, y={self.current_pose.y:.2f}, theta={self.current_pose.theta:.2f}')
        
        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = MoveToGoal()
    
    try:
        while rclpy.ok() and not node.goal_reached:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        node.get_logger().info('Node stopped by user')
    finally:
        # Останавливаем черепаху
        cmd = Twist()
        node.publisher.publish(cmd)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()