#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from cleaning_robot_interfaces.action import CleaningTask

class CleaningActionClient(Node):
    def __init__(self):
        super().__init__('cleaning_action_client')
        self.action_client = ActionClient(self, CleaningTask, 'CleaningTask')
        self.tasks = [
            {'type': 'clean_circle', 'area_size': 3.0, 'target_x': 0.0, 'target_y': 0.0},
            {'type': 'return_home', 'area_size': 0.0, 'target_x': 5.5, 'target_y': 5.5}
        ]
        self.current_task_idx = 0
        self.all_tasks_done = False

    def send_goal(self, task):
        goal_msg = CleaningTask.Goal()
        goal_msg.task_type = task['type']
        goal_msg.area_size = task['area_size']
        goal_msg.target_x = task['target_x']
        goal_msg.target_y = task['target_y']
        
        self.get_logger().info(f'Sending goal: {task["type"]}, area_size: {task["area_size"]}')
        self.action_client.wait_for_server()
        return self.action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback: Progress={feedback.progress_percent}%, Points={feedback.current_cleaned_points}, Pos=({feedback.current_x:.2f}, {feedback.current_y:.2f})')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return
        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: Success={result.success}, Points={result.cleaned_points}, Distance={result.total_distance:.2f}')
        self.current_task_idx += 1
        if self.current_task_idx < len(self.tasks):
            self.send_next_goal()
        else:
            self.all_tasks_done = True

    def send_next_goal(self):
        task = self.tasks[self.current_task_idx]
        send_goal_future = self.send_goal(task)
        send_goal_future.add_done_callback(self.goal_response_callback)

def main(args=None):
    rclpy.init(args=args)
    client = CleaningActionClient()
    client.send_next_goal()
    
    try:
        while rclpy.ok() and not client.all_tasks_done:
            rclpy.spin_once(client, timeout_sec=0.1)
    except KeyboardInterrupt:
        client.get_logger().info('Node stopped by user')
    finally:
        client.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()