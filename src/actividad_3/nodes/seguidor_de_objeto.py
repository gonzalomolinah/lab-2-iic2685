#!/usr/bin/env python3
import rclpy
import numpy as np
import cv2
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseArray
from cv_bridge import CvBridge
from geometry_msgs.msg import Vector3
import time

# La idea del nodo es
# recibe la posicion del cuadrado azul 
# calcila diferencia entre la posicion del cuadrado azul y la posicion del robot
# rota hacia esta 
# avanza con velocidad constante 

class SeguidorDeObjeto(Node): #? Modificar nombre de clase
    def __init__(self):
        super().__init__("seguidor_de_objeto") #? Modificar nombre del nodo
        self.center_x = 320.0 
        self.error_x = 0.0
        self.object_detected = False
        self.last_seen_time = None
        self.init_communications() #? Inicializa comunicaciones
        self.timer = self.create_timer(0.1, self.rotate_robot_towards_blue_square) #? Crear temporizador para el bucle de control   
    def setup_parameters(self): #? Inicializar parámetros de ejecución
        pass
    
    def init_communications(self): #? Crear Comunicaciones (Tópicos/Servicios)
        topic = '/blue_square_position' #? Subscritor de la cámara
        self.subscription = self.create_subscription(
            Vector3, #? Tipo de mensaje
            topic, #? Nombre del tópico
            self.get_position, #? Callback
            10) #? Tamaño de la cola
        ### CONTROLADOR PROVISIONAL 
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10) #? Publicador de velocidad del robot
    # Encontrada la poscion, procesamos la imagen, para eventualmente girar el robot hacia el cuadrado azul
    def rotate_robot_towards_blue_square(self):
        cmd = Twist()
        if not self.object_detected: self.publisher.publish(cmd); return 
        if (self.last_seen_time is None or time.monotonic() - self.last_seen_time > 0.5):
            self.object_detected = False
            self.publisher.publish(cmd)
            return
        if abs(self.error_x) < 15:
            cmd.angular.z = 0.0
        elif self.error_x > 0: # a la derecha del centro, giramos a la derecha
            cmd.angular.z = -0.2
        elif self.error_x < 0: # a la izquierda del centro, giramos a la izquierda
            cmd.angular.z = 0.2

        # aca llamar a move_robot_towards_blue_square dsp 
        cmd.linear.x = 0.0
        self.publisher.publish(cmd)

    #movemos el robot hacia el cuadrado azul
    def move_robot_towards_blue_square(self, vector):
        pass
    def get_position(self, msg):
        self.error_x = msg.x - self.center_x
        self.object_detected = True
        self.last_seen_time = time.monotonic()

def main(args=None):
    rclpy.init(args=args) #? Inicializa ROS
    node = SeguidorDeObjeto() #? Instancia de un nodo de clase SeguidorDeObjeto
    node.setup_parameters() #? Inicializa parámetros de ejecución
    rclpy.spin(node) #? Permite ejecución continua de un nodo
    rclpy.shutdown() #? Cierra el nodo al terminar la ejecución
    
    
    
if __name__ == "__main__":
    main()



# kinect data
# encodding: 32FC1
# height: 480
# width: 640
# step: 2560
