#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseArray
from tf_transformations import euler_from_quaternion, quaternion_from_euler
import os
import time

CTE_X = 0.2 
CTE_W = 1.0
RUTA_POSES = os.path.join(os.path.dirname(__file__), 'poses.txt')

time.sleep(3.0)

class PoseLoader(Node):
    def __init__(self):
        super().__init__('pose_loader')
        self.pose_publisher = self.create_publisher(PoseArray, '/goal_list', 10)
        self.timer = self.create_timer(1.0, self.publish_poses)
        self.waiting = False

    def publish_poses(self):
        self.timer.cancel()
        pose_array = PoseArray()
        try:
            with open(RUTA_POSES, 'r') as f:
                for linea in f:
                    self.get_logger().info(f"Pose leída: {linea.strip()}")
                    linea = linea.strip()[1:-1]
                    self.get_logger().info(f"Pose procesada: {linea}")

                    x, y, theta = map(float, linea.split(','))
                    self.get_logger().info(f"Pose convertida: x={x}, y={y}, theta={theta}")

                    pose = Pose()
                    pose.position.x = x
                    pose.position.y = y
                    pose.position.z = 0.0
                    quat = quaternion_from_euler(0, 0, theta)
                    pose.orientation.x = quat[0]
                    pose.orientation.y = quat[1]
                    pose.orientation.z = quat[2]
                    pose.orientation.w = quat[3]
                    pose_array.poses.append(pose)
            self.pose_publisher.publish(pose_array)
        except Exception as e:
            self.get_logger().error(f"Error al leer las poses: {e}")
        
        finally:
            self.get_logger().info("Publicación de poses completada. Deteniendo el nodo.")
            self.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    rclpy.init()
    pose_loader = PoseLoader()
    rclpy.spin(pose_loader)
    pose_loader.destroy_node()
    rclpy.shutdown()
