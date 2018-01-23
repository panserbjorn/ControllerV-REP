import vrep
import time
import math 
import numpy as np
import secuenceGenerator as sg

#TODO Hacer genérico para que sirva para cualquier base y cualquier cnatidad de opciones
def decimalToOneHot(decimal):
	oneHot = [0,0,0,0]
	if (decimal/27 >= 2 ):
		oneHot[0] = 1
	elif (deimal /27 < 1):
		oneHot[0] = -1
	decimal = decimal % 27
	if (decimal/9 >= 2 ):
		oneHot[1] = 1
	elif (deimal /9 < 1):
		oneHot[1] = -1
	decimal = decimal %9
	if (decimal/3 >= 2 ):
		oneHot[2] = 1
	elif (deimal /3 < 1):
		oneHot[2] = -1
	oneHot[3] = decimal%3
	return oneHot



def recoverRobotParts(clientID):
	#Recover the handles for the motors
	LUMRetCode, LUM = vrep.simxGetObjectHandle(clientID, "LUM", vrep.simx_opmode_blocking)
	LLMRetCode, LLM = vrep.simxGetObjectHandle(clientID, "LLM", vrep.simx_opmode_blocking)
	RUMRetCode, RUM = vrep.simxGetObjectHandle(clientID, "RUM", vrep.simx_opmode_blocking)
	RLMRetCode, RLM = vrep.simxGetObjectHandle(clientID, "RLM", vrep.simx_opmode_blocking)

def setVelocity(clientID, motorHandle, targetVelocity):
	vrep.simxSetJointTargetVelocity(clientID, motorHandle, targetVelocity, vrep.simx_opmode_oneshot)

def getPosition(clientID, objectID)
	return vrep.simxGetObjectPosition(clientID, objectID, -1, vrep.simx_opmode_oneshot)

class myEnv():
	portNumb
	logFileName
	actions
	score
	hasfallen
	LUM
	LLM
	RUM
	RLM
	head
	LUMSpeed
	LLMSpeed
	RUMSpeed
	RLMSpeed
	clientID


	'''
	TOOD debería conectarme con el simulador en el init
	Así de esta manera puedo controlar las cosas y poder devolver lo que hacen los otro métodos

	'''
	def _init_():
		self.portNumb = 19997
		self.actions = []
		self.score = 0
		self.hasfallen = False
		self.LUMSpeed = 0
		self.LLMSpeed = 0 
		self.RUMSpeed = 0 
		self.RLMSpeed = 0
		self.clientID = vrep.simxStart('127.0.0.1', portNumb, True, True, 5000, 5)
		if clientID != -1 :
		print ("se pudo establecer la conexión con la api del simulador")
		self.LUM,self.LLM,self.RUM,self.RLM,self.head = recoverRobotParts(clientID)
		setVelocity(clientID,LUM,LUMSpeed)
		setVelocity(clientID,LLM,LLMSpeed)
		setVelocity(clientID,RUM,RUMSpeed)
		setVelocity(clientID,RLM,RLMSpeed)

	'''
	TODO
	Este método debería devolver las posiciones y las velocidades de las partes del robot, no la cantidad de variables a devolver

	'''
	def observation_space():
		#Son las 4 posiciones, más las 4 velocidades de los motores
		#Más la posición de la cabez y la velocidad de la cabeza en el eje x
		#TODO ver si esto no da problemas por el hecho de que la posición es una terna y las velocidades son números
		return [getPosition(clientID,LUM),getPosition(clientID,LLM),getPosition(clientID,RUM),getPosition(clientID,RLM),LLMSpeed,LUMSpeed,RLMSpeed,RUMSpeed]

	'''
	Este método debería devolver las acciones posibles en lugar de solo la cantidad de acciones que se pueden realizar
	'''
	def action_space():
		#Son las 64 configuraciones que pueden tener los motres (son 4 motores y 3 estados [apagado, encendido positivo, encendido negativo], así que es 4^3)
		#return 4^3
		return range(3^4)


	'''
	Este método recibe ua acción y debería realizarla durante el próximo perído de tiempo de acción

	Retorna 
		- observaciones array dim = 10
		- reward si la acción fue positiva o negativa (diferencia del puntaje con el score)
		- done (si se terminaron la cantidad de acciónes posibles o si el robot se ha caído)
	'''
	def step(action):
		codedAction = decimalToOneHot(action)
		actions += action

		

	'''
	Este método reinicia la simulación
	'''
	def reset():

	



