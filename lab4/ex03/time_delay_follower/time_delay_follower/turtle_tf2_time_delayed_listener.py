import rclpy
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener
from geometry_msgs.msg import Twist
import math

class TimeTravelFollower(Node):
    def __init__(self):
        super().__init__('turtle_time_traveler')
        
        # Параметр задержки
        self.declare_parameter('delay', 5.0)
        self.delay = self.get_parameter('delay').value
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.cmd_pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 1)
        
        # Таймер
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        self.get_logger().info(f'Time travel follower started with delay: {self.delay} seconds')

    def timer_callback(self):
        now = self.get_clock().now()
        past_time = now - rclpy.duration.Duration(seconds=self.delay)
        
        try:
            # Даем время системам инициализироваться
            if now.nanoseconds / 1e9 < 3.0:  # Ждем 3 секунды после старта
                return
                
            # Ищем позицию turtle1 в прошлом относительно мира
            trans = self.tf_buffer.lookup_transform(
                'world',
                'turtle1',  
                past_time,
                timeout=rclpy.duration.Duration(seconds=1.0)
            )
            
            # Получаем текущую позицию turtle2 относительно мира
            trans_turtle2 = self.tf_buffer.lookup_transform(
                'world',
                'turtle2', 
                Time(),
                timeout=rclpy.duration.Duration(seconds=1.0)
            )
            
            twist = Twist()
            
            # Вычисляем разницу между текущей позицией turtle2 и прошлой позицией turtle1
            dx = trans.transform.translation.x - trans_turtle2.transform.translation.x
            dy = trans.transform.translation.y - trans_turtle2.transform.translation.y
            
            distance = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)
            
            # Вычисляем разницу в угле между текущим направлением turtle2 и целевым направлением
            current_theta = 2 * math.atan2(trans_turtle2.transform.rotation.z, 
                                        trans_turtle2.transform.rotation.w)
            angle_diff = angle - current_theta
            
            # Нормализуем разницу углов
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            if distance > 0.5:
                twist.linear.x = min(1.0, distance * 0.5)
                twist.angular.z = 2.0 * angle_diff
            else:
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                
            self.get_logger().info(f'Distance: {distance:.2f}, Angle: {angle_diff:.2f}, Linear: {twist.linear.x:.2f}, Angular: {twist.angular.z:.2f}')
            self.cmd_pub.publish(twist)
            
        except Exception as e:
            self.get_logger().warn(f'TF error: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = TimeTravelFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()