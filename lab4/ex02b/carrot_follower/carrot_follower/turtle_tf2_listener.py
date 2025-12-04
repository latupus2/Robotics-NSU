import math
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class TurtleTf2Listener(Node):
    def __init__(self):
        super().__init__('turtle_tf2_listener')

        # Параметры
        self.target_frame = self.declare_parameter(
            'target_frame', 'carrot1').get_parameter_value().string_value  # Наше имя фрейма

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Издатель для управления turtle2
        self.publisher = self.create_publisher(Twist, 'turtle2/cmd_vel', 1)

        # Таймер для управления
        self.timer = self.create_timer(0.1, self.on_timer)  # Более частая частота
        
        self.get_logger().info(f'Turtle listener started, following {self.target_frame}')

    def on_timer(self):
        from_frame_rel = self.target_frame
        to_frame_rel = 'turtle2'

        try:
            t = self.tf_buffer.lookup_transform(
                to_frame_rel,
                from_frame_rel,
                rclpy.time.Time())
        except TransformException as ex:
            self.get_logger().info(
                f'Could not transform {to_frame_rel} to {from_frame_rel}: {ex}')
            return

        msg = Twist()
        scale_rotation_rate = 1.0
        msg.angular.z = scale_rotation_rate * math.atan2(
            t.transform.translation.y,
            t.transform.translation.x)

        scale_forward_speed = 0.5
        msg.linear.x = scale_forward_speed * math.sqrt(
            t.transform.translation.x ** 2 +
            t.transform.translation.y ** 2)

        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = TurtleTf2Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()