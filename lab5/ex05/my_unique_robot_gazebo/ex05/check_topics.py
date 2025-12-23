#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class TopicChecker(Node):
    def __init__(self):
        super().__init__('topic_checker')
        self.get_logger().info("Checking available topics...")
        self.timer = self.create_timer(2.0, self.check_topics)
    
    def check_topics(self):
        topics = self.get_topic_names_and_types()
        self.get_logger().info("="*50)
        for topic_name, topic_types in topics:
            if 'odom' in topic_name or 'joint' in topic_name or 'cmd_vel' in topic_name:
                self.get_logger().info(f"{topic_name}: {topic_types}")

def main(args=None):
    rclpy.init(args=args)
    node = TopicChecker()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()