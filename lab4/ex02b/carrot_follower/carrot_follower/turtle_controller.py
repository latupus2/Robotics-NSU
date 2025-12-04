import math
from geometry_msgs.msg import Twist
from target_carrot_interfaces.msg import TargetInfo
import rclpy
from rclpy.node import Node
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from rclpy.qos import qos_profile_system_default
import threading

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        
        # Параметры
        self.declare_parameter('switch_threshold', 1.0)
        self.switch_threshold = self.get_parameter('switch_threshold').value
        
        # Список целей в порядке переключения
        self.targets = ['carrot1', 'carrot2', 'static_target']
        self.current_target_index = 0
        self.current_target = self.targets[self.current_target_index]
        
        # TF2
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Издатель для управления turtle2
        self.publisher = self.create_publisher(Twist, 'turtle2/cmd_vel', 10)
        
        # Издатель информации о текущей цели
        self.target_info_pub = self.create_publisher(TargetInfo, '/current_target', 10)
        
        # Таймер для управления
        self.timer = self.create_timer(0.1, self.on_timer)
        
        # Флаг для переключения по нажатию клавиши
        self.manual_switch = False
        
        # Запускаем поток для чтения клавиатуры
        self.keyboard_thread = threading.Thread(target=self.keyboard_listener)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        
        self.get_logger().info(f'Turtle controller started')
        self.get_logger().info(f'Following target: {self.current_target}')
        self.get_logger().info(f'Press "n" to switch to next target')
        
    def keyboard_listener(self):
        """Поток для прослушивания нажатий клавиш"""
        while rclpy.ok():
            try:
                key = input()
                if key == 'n':
                    self.manual_switch = True
                    self.get_logger().info('Manual switch requested')
            except:
                pass
                
    def switch_to_next_target(self):
        """Переключение на следующую цель"""
        self.current_target_index = (self.current_target_index + 1) % len(self.targets)
        self.current_target = self.targets[self.current_target_index]
        self.get_logger().info(f'Switched to target: {self.current_target}')
        
    def on_timer(self):
        # Проверяем ручное переключение
        if self.manual_switch:
            self.switch_to_next_target()
            self.manual_switch = False
            
        from_frame_rel = self.current_target
        to_frame_rel = 'turtle2'
        
        try:
            # Получаем трансформацию от turtle2 к цели
            t = self.tf_buffer.lookup_transform(
                to_frame_rel,
                from_frame_rel,
                rclpy.time.Time())
        except TransformException as ex:
            self.get_logger().info(
                f'Could not transform {to_frame_rel} to {from_frame_rel}: {ex}')
            return
        
        # Вычисляем расстояние до цели
        distance = math.sqrt(
            t.transform.translation.x ** 2 +
            t.transform.translation.y ** 2)
        
        # Проверяем автоматическое переключение
        if distance < self.switch_threshold:
            self.switch_to_next_target()
            return
            
        # Публикуем информацию о текущей цели
        target_info = TargetInfo()
        target_info.target_name = self.current_target
        target_info.target_x = -t.transform.translation.x  # Преобразуем обратно в мировые координаты
        target_info.target_y = -t.transform.translation.y
        target_info.distance_to_target = distance
        self.target_info_pub.publish(target_info)
        
        # Управление turtle2 (PID-подобный контроллер)
        msg = Twist()
        
        # Угол к цели
        angle_to_target = math.atan2(
            t.transform.translation.y,
            t.transform.translation.x)
        
        # Линейная скорость (уменьшаем при приближении к цели)
        scale_forward_speed = 0.5
        msg.linear.x = scale_forward_speed * min(distance, 1.0)
        
        # Угловая скорость (поворот к цели)
        scale_rotation_rate = 2.0
        msg.angular.z = scale_rotation_rate * angle_to_target
        
        # Ограничиваем максимальную угловую скорость
        max_angular = 1.5
        if msg.angular.z > max_angular:
            msg.angular.z = max_angular
        elif msg.angular.z < -max_angular:
            msg.angular.z = -max_angular
            
        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = TurtleController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()