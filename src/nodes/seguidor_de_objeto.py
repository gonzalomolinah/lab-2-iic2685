#!/usr/bin/env python3
import rclpy
import numpy as np
import cv2
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from skimage.measure import block_reduce
from geometry_msgs.msg import Vector3


# La idea del nodo es
# recibe la posicion del cuadrado azul 
# calcila diferencia entre la posicion del cuadrado azul y la posicion del robot
# rota hacia esta 
# avanza con velocidad constante 

class SeguidorDeObjeto(Node): #? Modificar nombre de clase
    def __init__(self):
        super().__init__("seguidor_de_objeto") #? Modificar nombre del nodo
        self.bridge = CvBridge() #? Inicializar puente de OpenCV
    def setup_parameters(self): #? Inicializar parámetros de ejecución
        pass
    
    def init_communications(self): #? Crear Comunicaciones (Tópicos/Servicios)
        topic = '/blue_square_postition' #? Subscritor de la cámara
        self.subscription = self.create_subscription(
            Image, #? Tipo de mensaje
            topic, #? Nombre del tópico
            self.get_image, #? Callback
            10) #? Tamaño de la cola
    # Encontrada la poscion, procesamos la imagen, para eventualmente girar el robot hacia el cuadrado azul
    def rotate_robot_towards_blue_square(self, vector):
        pass
    #movemos el robot hacia el cuadrado azul
    def move_robot_towards_blue_square(self, vector):
        pass


def main(args=None):
    rclpy.init(args=args) #? Inicializa ROS
    node = SeguidorDeObjeto() #? Instancia de un nodo de clase SeguidorDeObjeto
    node.init_communications() #? Inicializa comunicaciones
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
