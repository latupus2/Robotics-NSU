import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
from turtlesim.msg import Pose
import math

class TurtleTFBroadcaster(Node):
    def __init__(self):
        super().__init__('turtle_tf_broadcaster')
        # Получаем имя черепахи из параметра
        self.declare_parameter('turtle_name', 'turtle1')
        self.turtle_name = self.get_parameter('turtle_name').get_parameter_value().string_value
        
        self.broadcaster = TransformBroadcaster(self)
        self.subscription = self.create_subscription(
            Pose,
            f'/{self.turtle_name}/pose',
            self.handle_pose,
            1
        )
        self.get_logger().info(f'Starting TF broadcaster for {self.turtle_name}')

    def handle_pose(self, msg):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = self.turtle_name
        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0
        q = self.euler_to_quaternion(0, 0, msg.theta)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        
        self.broadcaster.sendTransform(t)
        # Логируем с троттлингом, чтобы не засорять консоль
        self.get_logger().info(f'Published transform for {self.turtle_name} at ({msg.x:.2f}, {msg.y:.2f})', 
                               throttle_duration_sec=2.0)

    def euler_to_quaternion(self, roll, pitch, yaw):
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
        return [x, y, z, w]

def main(args=None):
    rclpy.init(args=args)
    node = TurtleTFBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()