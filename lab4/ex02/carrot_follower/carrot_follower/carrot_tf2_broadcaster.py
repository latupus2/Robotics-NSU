import math
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster

class CarrotTf2Broadcaster(Node):
    def __init__(self):
        super().__init__('carrot_tf2_broadcaster')
        
        # Параметры
        self.declare_parameter('radius', 2.0)
        self.declare_parameter('direction_of_rotation', 1)
        
        self.radius = self.get_parameter('radius').value
        self.direction = self.get_parameter('direction_of_rotation').value
        self.angular_speed = 1.0  # рад/с

        self.tf_broadcaster = TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.broadcast_timer_callback)
        
        self.get_logger().info(f'Carrot broadcaster started with radius={self.radius}, direction={self.direction}')

    def broadcast_timer_callback(self):
        now = self.get_clock().now()
        time = now.nanoseconds / 1e9  # время в секундах

        # Вычисляем theta: для clockwise (1) - отрицательное, для ccw (-1) - положительное
        theta = -self.direction * self.angular_speed * time

        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = 'turtle1'
        t.child_frame_id = 'carrot1'  # Наше имя фрейма
        t.transform.translation.x = self.radius * math.cos(theta)
        t.transform.translation.y = self.radius * math.sin(theta)
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)

def main():
    rclpy.init()
    node = CarrotTf2Broadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()