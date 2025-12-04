import math
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from turtlesim.msg import Pose

class TurtleTf2Broadcaster(Node):
    def __init__(self):
        super().__init__('turtle_tf2_broadcaster')

        # Параметры
        self.turtlename = self.declare_parameter(
            'turtlename', 'turtle1').get_parameter_value().string_value  # Наше имя по умолчанию

        # Инициализируем широковещателя TF2
        self.tf_broadcaster = TransformBroadcaster(self)

        # Подписываемся на тему позы черепахи
        self.subscription = self.create_subscription(
            Pose,
            f'/{self.turtlename}/pose',
            self.handle_turtle_pose,
            1)
        
        self.get_logger().info(f'Broadcasting transforms for {self.turtlename}')

    def handle_turtle_pose(self, msg):
        t = TransformStamped()

        # Заполняем заголовок трансформации
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = self.turtlename

        # Позиция
        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0

        # Ориентация из угла theta
        # Упрощенная формула для 2D (только вращение вокруг Z)
        theta = msg.theta
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(theta / 2.0)
        t.transform.rotation.w = math.cos(theta / 2.0)

        # Отправляем трансформацию
        self.tf_broadcaster.sendTransform(t)

def main():
    rclpy.init()
    node = TurtleTf2Broadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()