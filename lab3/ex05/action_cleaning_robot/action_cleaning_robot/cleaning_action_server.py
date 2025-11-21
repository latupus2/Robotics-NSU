#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
from cleaning_robot_interfaces.action import CleaningTask

class CleaningActionServer(Node):
    def __init__(self):
        super().__init__('cleaning_action_server')
        self.action_server = ActionServer(
            self, CleaningTask, 'CleaningTask', self.execute_callback)
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)
        self.current_pose = Pose()
        self.cleaned_points = 0
        self.total_distance = 0.0
        self.last_x = 0.0
        self.last_y = 0.0
        self.is_first_pose = True
        # ПИД-константы
        self.linear_kp = 1.0
        self.angular_kp = 2.0
        self.tolerance = 0.1
        self.angular_tolerance = 0.05
        self.grid_step = 0.5  # Шаг для зигзаг в квадрате (меньше — плотнее покрытие)

    def pose_callback(self, msg):
        self.current_pose = msg
        if self.is_first_pose:
            self.last_x = msg.x
            self.last_y = msg.y
            self.is_first_pose = False
        else:
            dx = msg.x - self.last_x
            dy = msg.y - self.last_y
            dist = math.sqrt(dx**2 + dy**2)
            self.total_distance += dist
            self.cleaned_points += int(dist / 0.1)  # Каждые 0.1 м = 1 "убранная" точка
            self.last_x = msg.x
            self.last_y = msg.y

    def execute_callback(self, goal_handle):
        self.get_logger().info(f'Received goal: {goal_handle.request.task_type}, area_size: {goal_handle.request.area_size}')
        feedback_msg = CleaningTask.Feedback()
        result = CleaningTask.Result()
        result.success = False
        
        # Сбрасываем счетчики ПЕРЕД началом задачи
        self.cleaned_points = 0
        self.total_distance = 0.0
        self.is_first_pose = True  # ⬅️ СБРАСЫВАЕМ ДЛЯ ПРАВИЛЬНОГО ПОДСЧЕТА РАССТОЯНИЯ

        task_type = goal_handle.request.task_type
        area_size = goal_handle.request.area_size

        if task_type == 'clean_square':
            success = self.clean_square(goal_handle, area_size, feedback_msg)
        elif task_type == 'clean_circle':
            success = self.clean_circle(goal_handle, area_size, feedback_msg)
        elif task_type == 'return_home':
            success = self.return_home(goal_handle, feedback_msg)
        else:
            self.get_logger().error('Unknown task type')
            goal_handle.abort()
            return result

        result.success = success
        result.cleaned_points = self.cleaned_points  # ⬅️ ТЕПЕРЬ ЗДЕСЬ БУДУТ ВИРТУАЛЬНЫЕ ТОЧКИ
        result.total_distance = self.total_distance
        
        if success:
            goal_handle.succeed()
        else:
            goal_handle.abort()
        
        return result

    def clean_square(self, goal_handle, size, feedback_msg):
        start_x = self.current_pose.x
        start_y = self.current_pose.y
        num_steps = int(size / self.grid_step)
        total_virtual_points = num_steps * 10
        
        for i in range(num_steps + 1):
            if not goal_handle.is_active:
                return False
                
            goal_x = start_x + size if i % 2 == 0 else start_x
            goal_y = start_y + i * self.grid_step
            
            goal_x = max(0.5, min(10.5, goal_x))
            goal_y = max(0.5, min(10.5, goal_y))
            
            self.move_to_point(goal_x, goal_y, feedback_msg, goal_handle)
            
            # ВИРТУАЛЬНЫЕ ТОЧКИ ДЛЯ ФИДБЕКА И РЕЗУЛЬТАТА
            self.cleaned_points = int((i + 1) / num_steps * total_virtual_points)  # ⬅️ ОБНОВЛЯЕМ НАПРЯМУЮ
            
            feedback_msg.progress_percent = int((i + 1) / num_steps * 100)
            feedback_msg.current_cleaned_points = self.cleaned_points  # ⬅️ ИСПОЛЬЗУЕМ self.cleaned_points
            feedback_msg.current_x = self.current_pose.x
            feedback_msg.current_y = self.current_pose.y
            goal_handle.publish_feedback(feedback_msg)
        
        self.move_to_point(start_x, start_y, feedback_msg, goal_handle)
        return True

    def clean_circle(self, goal_handle, radius, feedback_msg):
        center_x = self.current_pose.x
        center_y = self.current_pose.y
        num_loops = int(radius / self.grid_step)
        total_virtual_points = num_loops * 20
        
        for i in range(num_loops, 0, -1):
            if not goal_handle.is_active:
                return False
            
            current_radius = i * self.grid_step
            num_points = int(2 * math.pi * current_radius / self.grid_step)
            
            for j in range(num_points + 1):
                if not goal_handle.is_active:
                    return False
                
                angle = 2 * math.pi * j / num_points
                goal_x = center_x + current_radius * math.cos(angle)
                goal_y = center_y + current_radius * math.sin(angle)
                
                goal_x = max(0.5, min(10.5, goal_x))
                goal_y = max(0.5, min(10.5, goal_y))
                
                self.move_to_point(goal_x, goal_y, feedback_msg, goal_handle)
            
            # ВИРТУАЛЬНЫЕ ТОЧКИ
            progress = (num_loops - i + 1) / num_loops
            self.cleaned_points = int(progress * total_virtual_points)  # ⬅️ ОБНОВЛЯЕМ НАПРЯМУЮ
            
            feedback_msg.progress_percent = int(progress * 100)
            feedback_msg.current_cleaned_points = self.cleaned_points  # ⬅️ ИСПОЛЬЗУЕМ self.cleaned_points
            feedback_msg.current_x = self.current_pose.x
            feedback_msg.current_y = self.current_pose.y
            goal_handle.publish_feedback(feedback_msg)
        
        self.move_to_point(center_x, center_y, feedback_msg, goal_handle)
        return True

    def return_home(self, goal_handle, feedback_msg):
        goal_x = goal_handle.request.target_x
        goal_y = goal_handle.request.target_y
        self.move_to_point(goal_x, goal_y, feedback_msg, goal_handle)
        feedback_msg.progress_percent = 100
        feedback_msg.current_cleaned_points = self.cleaned_points
        feedback_msg.current_x = self.current_pose.x
        feedback_msg.current_y = self.current_pose.y
        goal_handle.publish_feedback(feedback_msg)
        goal_handle.succeed()

    def move_to_point(self, goal_x, goal_y, feedback_msg, goal_handle):
        cmd = Twist()
        while rclpy.ok() and goal_handle.is_active:
            dx = goal_x - self.current_pose.x
            dy = goal_y - self.current_pose.y
            distance = math.sqrt(dx**2 + dy**2)
            angle_to_goal = math.atan2(dy, dx)
            angle_error = angle_to_goal - self.current_pose.theta
            
            while angle_error > math.pi:
                angle_error -= 2 * math.pi
            while angle_error < -math.pi:
                angle_error += 2 * math.pi
            
            # Сначала поворот на месте
            if abs(angle_error) > self.angular_tolerance:
                cmd.linear.x = 0.0
                cmd.angular.z = self.angular_kp * angle_error
                cmd.angular.z = min(max(cmd.angular.z, -4.0), 4.0)
            else:
                # Затем прямолинейное движение
                cmd.angular.z = 0.0
                if distance > self.tolerance:
                    cmd.linear.x = self.linear_kp * distance
                    cmd.linear.x = min(max(cmd.linear.x, -2.0), 2.0)
                else:
                    cmd.linear.x = 0.0
            
            self.publisher.publish(cmd)
            
            if distance <= self.tolerance and abs(angle_error) <= self.angular_tolerance:
                break
            
            feedback_msg.current_x = self.current_pose.x
            feedback_msg.current_y = self.current_pose.y
            goal_handle.publish_feedback(feedback_msg)
            rclpy.spin_once(self, timeout_sec=0.1)
        # Останавливаем черепаху после достижения точки
        cmd = Twist()
        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    server = CleaningActionServer()
    rclpy.spin(server)
    server.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()