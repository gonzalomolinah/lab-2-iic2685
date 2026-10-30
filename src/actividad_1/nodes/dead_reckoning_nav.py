#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseArray
from tf_transformations import euler_from_quaternion, quaternion_from_euler
import threading
import time
import math
CTE_X = 0.2 
CTE_W = 1.0
CTE_T = 1.11

time.sleep(2.0)

class DeadReckoningNav(Node):
    def __init__(self):
        super().__init__('dead_reckoning_nav')
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.goal_pose_subscriber = self.create_subscription(PoseArray, '/goal_list', self.accion_mover_cb, 10)
        self.posicion_actual = (0.0, 0.0, 0.0)  # (x, y, theta)
        self.waiting = False
        self.movement_thread = None
        #self.timer = self.create_timer(1.0, self.probar2)
       
    def stop_robot(self):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_publisher.publish(twist)

    def aplicar_velocidad(self, speed_command_list):
        try:
            for v, w, t in speed_command_list:
                twist = Twist()
                twist.linear.x = v
                twist.angular.z = w
                factor = 1.0 if w == 0 else CTE_T

                inicio = time.time()
                moving_time = 0.0
                dt= 0.1
                while time.time() - inicio < t * factor:
                    self.cmd_vel_publisher.publish(twist)
                    #time.sleep(dt)
                    #moving_time += dt
                self.posicion_actual = self.actualizar_posicion(self.posicion_actual, v, w, t)
        finally:
            self.stop_robot()

    def actualizar_posicion(self, current_pos, v, w, t):
        x, y, theta = current_pos
        if w == 0:
            x += v * t * math.cos(theta)
            y += v * t * math.sin(theta)
        else:
            x += (v / w) * (math.sin(theta + w * t) - math.sin(theta))
            y += (v / w) * (-math.cos(theta + w * t) + math.cos(theta))
            theta += w * t

        return (x, y, theta)

    def mover_robot_a_destino(self, goal_pose):
        x_goal, y_goal, theta_goal = goal_pose
        x_current, y_current, theta_current = self.posicion_actual

        dx = x_goal - x_current
        dy = y_goal - y_current
        lista_movimientos = []
        angulo_referencia = theta_current

        self.get_logger().info(f"Moviendose a destino: {goal_pose}, desde: {self.posicion_actual}")
        self.get_logger().info(f"Diferencia: dx={dx}, dy={dy}, dtheta={theta_goal - theta_current}")

        # Recorrer primero el eje x y luego el eje y
        if dx > 0:
            dtheta = (0.0 - angulo_referencia) % (2 * math.pi)
            lista_movimientos.append((0.0, 1.0, dtheta))
            angulo_referencia += dtheta
        elif dx < 0:
            dtheta = (math.pi - angulo_referencia) % (2 * math.pi)
            lista_movimientos.append((0.0, 1.0, dtheta))
            angulo_referencia += dtheta
        
        lista_movimientos.append((0.2, 0.0, abs(dx) / 0.2))

        if dy > 0:
            dtheta = (math.pi / 2 - angulo_referencia) % (2 * math.pi)
            lista_movimientos.append((0.0, 1.0, dtheta))
            angulo_referencia += dtheta
        
        elif dy < 0:
            dtheta = (3 * math.pi / 2 - angulo_referencia) % (2 * math.pi)
            lista_movimientos.append((0.0, 1.0, dtheta))
            angulo_referencia += dtheta
        
        lista_movimientos.append((0.2, 0.0, abs(dy) / 0.2))

        dtheta = (theta_goal - angulo_referencia) % (2 * math.pi)
        lista_movimientos.append((0.0, 1.0, dtheta))

        self.get_logger().info(f"Lista de movimientos: {lista_movimientos}")
        for movimiento in lista_movimientos:
            self.aplicar_velocidad([movimiento])
            self.aplicar_velocidad([movimiento])

    def ejecutar_movimiento(self, msg):
        for pose in msg.poses:
            quat = (pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w)
            _, _, theta = euler_from_quaternion(quat)
            goal_pose = (pose.position.x, pose.position.y, theta)
            self.mover_robot_a_destino(goal_pose)
    def accion_mover_cb(self, msg):
        self.movement_thread = threading.Thread(target=self.ejecutar_movimiento, args=(msg,))
        self.movement_thread.start()

    def probar1(self):
        self.timer.cancel()
        comandos = [
            (0.2, 0.0, 2.0),
            (0.0, 1.0, 3.14),
            (0.2, 0.0, 2.0),
            (0.0, -1.0, 3.14), ]
        self.aplicar_velocidad(comandos)

    def probar2(self):
        self.timer.cancel()
        for _ in range(2):
            continue
            goal_pose = (1.0, 0.0, 0.0)
            self.mover_robot_a_destino(goal_pose)
            goal_pose = (1.0, 1.0, 0.0)
            self.mover_robot_a_destino(goal_pose)
            goal_pose = (0.0, 1.0, 0.0)
            self.mover_robot_a_destino(goal_pose)
            goal_pose = (0.0, 0.0, 0.0)
            self.mover_robot_a_destino(goal_pose)

def main():
    rclpy.init()
    node = DeadReckoningNav()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()