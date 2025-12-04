import math
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster

class TargetSwitcher(Node):
    def __init__(self):
        super().__init__('target_switcher')
        
        # Параметры
        self.declare_parameter('radius', 2.0)
        self.declare_parameter('direction_of_rotation', 1)
        self.declare_parameter('switch_threshold', 1.0)
        
        self.radius = self.get_parameter('radius').value
        self.direction = self.get_parameter('direction_of_rotation').value
        self.angular_speed = 1.0  # рад/с
        
        self.tf_broadcaster = TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.broadcast_timer_callback)
        
        # Статическая цель
        self.static_target_x = 8.0
        self.static_target_y = 2.0
        
        self.get_logger().info('Target switcher started')
        self.get_logger().info(f'Publishing targets: carrot1, carrot2, static_target')
        
    def broadcast_timer_callback(self):
        now = self.get_clock().now()
        time = now.nanoseconds / 1e9  # время в секундах
        
        # 1. Carrot1 - вращается вокруг turtle1
        theta1 = -self.direction * self.angular_speed * time
        
        t1 = TransformStamped()
        t1.header.stamp = now.to_msg()
        t1.header.frame_id = 'turtle1'
        t1.child_frame_id = 'carrot1'
        t1.transform.translation.x = self.radius * math.cos(theta1)
        t1.transform.translation.y = self.radius * math.sin(theta1)
        t1.transform.translation.z = 0.0
        t1.transform.rotation.x = 0.0
        t1.transform.rotation.y = 0.0
        t1.transform.rotation.z = 0.0
        t1.transform.rotation.w = 1.0
        
        # 2. Carrot2 - вращается вокруг turtle3 (используем тот же радиус, но противоположное направление)
        theta2 = self.direction * self.angular_speed * time  # Противоположное направление
        
        t2 = TransformStamped()
        t2.header.stamp = now.to_msg()
        t2.header.frame_id = 'turtle3'
        t2.child_frame_id = 'carrot2'
        t2.transform.translation.x = self.radius * math.cos(theta2)
        t2.transform.translation.y = self.radius * math.sin(theta2)
        t2.transform.translation.z = 0.0
        t2.transform.rotation.x = 0.0
        t2.transform.rotation.y = 0.0
        t2.transform.rotation.z = 0.0
        t2.transform.rotation.w = 1.0
        
        # 3. Static target - фиксированная позиция в мире
        t3 = TransformStamped()
        t3.header.stamp = now.to_msg()
        t3.header.frame_id = 'world'
        t3.child_frame_id = 'static_target'
        t3.transform.translation.x = self.static_target_x
        t3.transform.translation.y = self.static_target_y
        t3.transform.translation.z = 0.0
        t3.transform.rotation.x = 0.0
        t3.transform.rotation.y = 0.0
        t3.transform.rotation.z = 0.0
        t3.transform.rotation.w = 1.0
        
        # Отправляем все трансформации
        self.tf_broadcaster.sendTransform(t1)
        self.tf_broadcaster.sendTransform(t2)
        self.tf_broadcaster.sendTransform(t3)

def main():
    rclpy.init()
    node = TargetSwitcher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()