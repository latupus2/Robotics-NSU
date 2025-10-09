
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

class TextToCmdVel(Node):
    def __init__(self):
        super().__init__('text_to_cmd_vel')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            String,
            'cmd_text',
            self.text_callback,
            10
        )
        
        self.get_logger().info('TextToCmdVel node started, listening to cmd_text topic')

    def text_callback(self, msg):
        twist = Twist()
        command = msg.data.lower()  # Convert command to lowercase for consistency
        
        if command == 'move_forward':
            twist.linear.x = 1.0  # Move forward at 1 m/s
        elif command == 'move_backward':
            twist.linear.x = -1.0  # Move backward at 1 m/s
        elif command == 'turn_left':
            twist.angular.z = 1.5  # Turn left at 1.5 rad/s
        elif command == 'turn_right':
            twist.angular.z = -1.5  # Turn right at 1.5 rad/s
        else:
            self.get_logger().warn(f'Unknown command: {command}')
            return
        
        self.publisher_.publish(twist)
        self.get_logger().info(f'Published Twist: linear.x={twist.linear.x}, angular.z={twist.angular.z}')

def main(args=None):
    rclpy.init(args=args)
    node = TextToCmdVel()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
