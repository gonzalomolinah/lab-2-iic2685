#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion, quaternion_from_euler
import os

RUTA_DATOS = os.path.join(os.path.dirname(__file__), 'datos.csv')


class DataLogger(Node):
    def __init__(self):
        super().__init__('data_logger')
        self.odom_subscriber = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.pose_subscriber = self.create_subscription(Pose, '/real_pose', self.pose_callback, 10)

        self.timer = self.create_timer(0.1, self.log_data)

        with open(RUTA_DATOS, 'w') as f:
            f.write("x_odom,y_odom,theta_odom,x_real,y_real,theta_real\n")

        self.last_odom = None
        self.last_real_pose = None

    def odom_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        quat = (orientation.x, orientation.y, orientation.z, orientation.w)
        _, _, theta = euler_from_quaternion(quat)

        self.last_odom = (position.x, position.y, theta)

    def pose_callback(self, msg):
        position = msg.position
        orientation = msg.orientation
        quat = (orientation.x, orientation.y, orientation.z, orientation.w)
        _, _, theta = euler_from_quaternion(quat)

        self.last_real_pose = (position.x, position.y, theta)

    def log_data(self):
        if self.last_odom is not None and self.last_real_pose is not None:
            x_odom, y_odom, theta_odom = self.last_odom
            x_real, y_real, theta_real = self.last_real_pose

            with open(RUTA_DATOS, 'a') as f:
                f.write(f"{x_odom},{y_odom},{theta_odom},{x_real},{y_real},{theta_real}\n")


def main():
    rclpy.init()
    data_logger = DataLogger()
    try:
        rclpy.spin(data_logger)
    except:
        pass
    

    data_logger.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
