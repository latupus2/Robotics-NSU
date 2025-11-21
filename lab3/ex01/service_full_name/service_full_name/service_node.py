#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from full_name_interfaces.srv import FullName


class FullNameService(Node):

    def __init__(self):
        super().__init__('service_name')
        self.srv = self.create_service(
            FullName, 
            'SummFullName', 
            self.combine_names_callback
        )
        self.get_logger().info('Service is ready to combine full names...')

    def combine_names_callback(self, request, response):
        # Получаем фамилию, имя и отчество из запроса
        last_name = request.last_name
        first_name = request.first_name
        middle_name = request.middle_name
        
        # Объединяем в полное имя
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        response.full_name = full_name
        
        self.get_logger().info(
            f'Received: {last_name}, {first_name}, {middle_name} -> '
            f'Full name: "{full_name}"'
        )
        
        return response


def main(args=None):
    rclpy.init(args=args)
    full_name_service = FullNameService()
    try:
        rclpy.spin(full_name_service)
    except KeyboardInterrupt:
        pass
    finally:
        full_name_service.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()