#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from full_name_interfaces.srv import FullName


class FullNameClient(Node):

    def __init__(self):
        super().__init__('client_name')
        self.cli = self.create_client(FullName, 'SummFullName')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.get_logger().info('Service client is ready!')

    def send_request(self, last_name, first_name, middle_name):
        request = FullName.Request()
        request.last_name = last_name
        request.first_name = first_name
        request.middle_name = middle_name
        
        self.future = self.cli.call_async(request)
        rclpy.spin_until_future_complete(self, self.future)
        
        return self.future.result()


def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) != 4:
        print("Usage: ros2 run service_full_name client_name <last_name> <first_name> <middle_name>")
        return
    
    last_name = sys.argv[1]
    first_name = sys.argv[2]
    middle_name = sys.argv[3]
    
    client = FullNameClient()
    
    try:
        response = client.send_request(last_name, first_name, middle_name)
        client.get_logger().info(
            f'Request: {last_name}, {first_name}, {middle_name}\n'
            f'Full name received: "{response.full_name}"'
        )
    except Exception as e:
        client.get_logger().error(f'Service call failed: {e}')
    finally:
        client.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()