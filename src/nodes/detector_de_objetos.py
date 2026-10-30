#!/usr/bin/env python3


import rclpy
import numpy as np
import cv2
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Vector3

class detectorDeObjeto(Node): #? ModificaObstacleDetectoObstacleDetectorrr nombre de clase
    def __init__(self):
        super().__init__("detector_de_objeto") #? Modificar nombre del nodo
        self.bridge = CvBridge() #? Inicializar puente de OpenCV
    #? --- Atributos ---
    def setup_parameters(self): #? Inicializar parámetros de ejecución
        pass
    
    def init_communications(self): #? Crear Comunicaciones (Tópicos/Servicios)
        topic = 'camera/rgb/image_color' #? Subscritor de la cámara
        self.subscription = self.create_subscription(
            Image, #? Tipo de mensaje
            topic, #? Nombre del tópico
            self.get_image, #? Callback
            10) #? Tamaño de la cola
        topic = '/blue_square_position' #? Crear publicador del cuadrado azul
        self.publisher = self.create_publisher(Vector3, topic, 10) #? Publicador de obstáculos detectados
    
    # ============== FUNCION ===============
    # El robot estara buscando constantemente si hay un un grupo de pixeles azules 
    # lo suficientemente  grande, si esto es asi, pasa a ser zona de interes.te 
    # Cuando lo encuentra va ala funcion de procesamiento
    # En la funcionde procesamienteo se confirma si es un cuadrado azul 
    # en caso de ser cuadrado azul se pasa la posicion al nodo de seguimiento de objeto
    # el cual sera el encargado de rotar y mover el robot hacia el cuadrado azul
    # buscamos el cuadrado azul si hay pixel azules
    def look_for_blue_square(self, image):
        # Procesamos la matriz entera para confirmar que un cuadrado
        # si lo es lo mandamos a la funcion de procesar la posicion del cuadrad 
        np_image = np.array(image)
        hsv_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2HSV)
        # Definimos el azul entre 140 a 240 en el espacio HSV h: 180-300 s: 40-100 v: 50-100 
        lower_cap_blue_color = np.array([90, 80, 40]) 
        upper_cap_blue_color = np.array([150, 255, 255])
        # recorremos la matriz de pixeles y vemos si estan en el rango de azul
        blue_pixels = cv2.inRange(hsv_image, lower_cap_blue_color, upper_cap_blue_color)
        # ================= PROBAR ====================== cantidad de pixeles para un cuadrado
        # si hay mas de 1000 pixeles azules, sospechamos cuadrado azul 
        # pasamos la imagen a una binaria 
        #binary_image = cv2.threshold(blue_pixels, 127, 255, cv2.THRESH_BINARY)[1]
        binary_image = blue_pixels
        if cv2.countNonZero(binary_image) > 1000:
            self.process_blue_square_position(binary_image)

    # Encontrada la poscion, procesamos la imagen, para eventualmente girar el robot hacia el cuadrado azul
    def process_blue_square_position(self, image):
        # buscamos los contornos de la imagen binaria para ver si hay cuadrados 
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # esta funcion es pura IA AJDKAS
        for contour in contours:
            # aproximamos el contorno a un poligono
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            # si el poligono tiene 4 vertices, es un cuadrado
            area = cv2.contourArea(contour)
            if len(approx) == 4 and cv2.isContourConvex(approx) and area > 1000:
                # obtenemos el centro del cuadrado
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    vector = Vector3()
                    vector.x = cX
                    vector.y = 0.0
                    vector.z = 0.0
                    self.get_logger().info(f"Blue square at position: ({cX}, {cY})")
                    ### ===== IMPORTANTE ====
                    # solo nos importa la coordenada x, hacemos 0 las otras 
                    self.publisher.publish(vector) # despues de toda la matematica publicamos el vector 
        pass  
    def get_image(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.look_for_blue_square(cv_image)


def main(args=None):
    rclpy.init(args=args) #? Inicializa ROS
    node = detectorDeObjeto() #? Instancia de un nodo de clase detectorDeObjeto
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
