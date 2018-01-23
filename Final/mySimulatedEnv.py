import vrep
import time
import math 
import numpy as np
import secuenceGenerator as sg


def distancia(puntoA, puntoB):
	return abs(puntoA[0]-puntoB[0])+ abs(puntoA[2]-puntoB[2])

def puntoMovil(tiempo):
	return ((tiempo*0.09)-1.5,0.03,0.8)

def calculateReward(prevObs, obs, numActions):
	time = numActions*0.05
	puntoMovil = puntoMovil(time)
	prevPos = prevObs[-1][1][0]
	actualPos = obs[-1][1][0]
	reward = distancia(prevPos,puntoMovil) - distancia(actualPos, puntoMovil)
	stillAliveBonus = 5
	return reward + stillAliveBonus


'''
Transforma una acción de base decimal a oneHot con base 3 para los 4 motores
'''
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

def hasFallen(headPosition):
	return headPosition[0] == 0 and headPosition[1][2]<0.65

'''
Devuelve los motores del robot
'''
def recoverRobotParts(clientID):
	#Recover the handles for the motors
	LUMRetCode, LUM = vrep.simxGetObjectHandle(clientID, "LUM", vrep.simx_opmode_blocking)
	LLMRetCode, LLM = vrep.simxGetObjectHandle(clientID, "LLM", vrep.simx_opmode_blocking)
	RUMRetCode, RUM = vrep.simxGetObjectHandle(clientID, "RUM", vrep.simx_opmode_blocking)
	RLMRetCode, RLM = vrep.simxGetObjectHandle(clientID, "RLM", vrep.simx_opmode_blocking)

'''
Cambia la velocidad de un motor en el simulador
'''
def setVelocity(clientID, motorHandle, targetVelocity):
	vrep.simxSetJointTargetVelocity(clientID, motorHandle, targetVelocity, vrep.simx_opmode_oneshot)

'''
Devuelve la posición de un objeto dentro del simulador
'''
def getPosition(clientID, objectID)
	return vrep.simxGetObjectPosition(clientID, objectID, -1, vrep.simx_opmode_oneshot)



class myEnv():
	portNumb
	#logFileName
	actions
	#score
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
	#1200 acciones está bien, es un minuto
	maxActions = 1200


	
	def _init_(self):
		self.portNumb = 19997
		self.actions = []
		self.score = 0
		self.hasfallen = False
		self.LUMSpeed = 0
		self.LLMSpeed = 0 
		self.RUMSpeed = 0 
		self.RLMSpeed = 0
		self.clientID = vrep.simxStart('127.0.0.1', self.portNumb, True, True, 5000, 5)
		if self.clientID != -1 :
		print ("se pudo establecer la conexión con la api del simulador")
		self.LUM,self.LLM,self.RUM,self.RLM,self.head = recoverRobotParts(self.clientID)
		setVelocity(self.clientID,self.LUM,self.LUMSpeed)
		setVelocity(self.clientID,self.LLM,self.LLMSpeed)
		setVelocity(self.clientID,self.RUM,self.RUMSpeed)
		setVelocity(self.clientID,self.RLM,self.RLMSpeed)
		#Set simulation to be Synchonous instead of Asynchronous
		vrep.simxSynchronous(self.clientID, True)
		#Start simulation if it didn't start
		vrep.simxStartSimulation(self.clientID,vrep.simx_opmode_blocking)
		vrep.simxSynchronousTrigger(self.clientID)
	'''
	Devuelve las observaciones del robot (estado):
		- Posición LUM
		- Posición LLM
		- Posición RUM
		- Posición RLM
		- Velocidad ángular del LLM
		- Velocidad ánguar del LUM
		- Velocidad ángular del RLM
		- Velocidad ángular del RUM
		- Posición de la cabeza
	'''
	def observation_space(self):
		#Son las 4 posiciones, más las 4 velocidades de los motores
		#Más la posición de la cabeza
		#TODO ver si esto no da problemas por el hecho de que la posición es una terna y las velocidades son números
		return [getPosition(self.clientID,self.LUM),getPosition(self.clientID,self.LLM),getPosition(self.clientID,self.RUM),getPosition(self.clientID,self.RLM),self.LLMSpeed,self.LUMSpeed,self.RLMSpeed,self.RUMSpeed, getPosition(self.clientID, self.head)]

	'''
	Devuelve un array con la lista de acciones posibles en base decimal
	'''
	def action_space():
		#Son las 64 configuraciones que pueden tener los motres (son 4 motores y 3 estados [apagado, encendido positivo, encendido negativo], así que es 4^3)
		#return 4^3
		return range(3^4)


	'''
	Este método recibe ua acción y debería realizarla durante el próximo perído de tiempo de acción

	Retorna 
		- observaciones array dim = 9
		- reward si la acción fue positiva o negativa (diferencia del puntaje con el score)
		- done (si se terminaron la cantidad de acciónes posibles o si el robot se ha caído)
	'''
	def step(self, action):
		codedAction = decimalToOneHot(action)
		self.actions += action
		previousObs = observation_space()
		moveRobot(codedAction)
		obs = observation_space()
		done = hasFallen(obs[-1]) || len(self.actions) > myEnv.maxActions	
		reward = calculateReward(previousObs, obs, len(self.actions))
		return (obs, reward, done)

		

	'''
	Este método reinicia la simulación
	'''
	def reset(self):
		self.actions = []
		self.hasFallen = False
		vrep.simxStopSimulation(self.clientID, vrep.simx_opmode_blocking)
		#This sleep is necesary for the simulation to finish stopping before starting again
		time.sleep(2)
		vrep.simxStartSimulation(self.clientID, vrep.simx_opmode_blocking)

	
	def advanceTime():
		vrep.simxSynchronousTrigger(self.clientID)

	def moveRobot(self, codedAction):
		setVelocity(self.clientID, self.LUM, codedAction[0])
		setVelocity(self.clientID, self.LLM, codedAction[1])
		setVelocity(self.clientID, self.RUM, codedAction[2])
		setVelocity(self.clientID, self.RLM, codedAction[3])
		advanceTime()


