import vrep
import time
import math 
import numpy as np
from RobotController import robotController
import yaml as y


def distance(pointA, pointB):
	return abs(pointA[0]-pointB[0])+ abs(pointA[2]-pointB[2])

def movingPoint(time_step):
	# return ((tiempo*0.09)-1.5,0.03,0.8) # Muy lento
	return ((time_step*0.1)-1.0,0.03,0.8) # Este arranca más adelante y además es más rápido

def calculateReward(prevObs, obs, numActions):
	#TODO ESTO ESTA MAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	# time = numActions*0.05
	# puntoM = movingPoint(time)
	prevHeadPos = prevObs['Head']
	actualHeadPos = obs['Head']
	# # print("posición Actual: ",actualPos)
	# # print('Punto Móvil: ', puntoM)
	# #TODO Verificar que el reward esté bien.
	# reward = (1/distance(actualPos, puntoM)) - (1/distance(prevPos,puntoM) )
	reward = actualHeadPos[0] - prevHeadPos[0]
	stillAliveBonus = 0.01
	return reward + stillAliveBonus


'''
Transforma una acción de base decimal a oneHot con base 3 para los 4 motores
'''
#TODO Hacer genérico para que sirva para cualquier base y cualquier cantidad de opciones
def decimalToOneHot(decimal,exp):

	oneHot = []
	for i in range(exp):
		oneHot.append(0)
	counter = exp
	while counter > 1:
		if (decimal/(3**(counter-1)) >= 2):
			oneHot[exp-counter] = 1
		elif (decimal/(3**(counter-1)) < 1):
			oneHot[exp-counter] = -1
		decimal = decimal % (3**(counter-1))
		counter-=1
	oneHot[exp-counter] = (decimal%3) -1
	# if (decimal/27 >= 2 ):
	# 	oneHot[0] = 1
	# elif (decimal /27 < 1):
	# 	oneHot[0] = -1
	# decimal = decimal % 27
	# if (decimal/9 >= 2 ):
	# 	oneHot[1] = 1
	# elif (decimal /9 < 1):
	# 	oneHot[1] = -1
	# decimal = decimal %9
	# if (decimal/3 >= 2 ):
	# 	oneHot[2] = 1
	# elif (decimal /3 < 1):
	# 	oneHot[2] = -1
	# oneHot[3] = (decimal%3) -1
	return oneHot

def hasFallen(obs):
	return obs['Head'][1][2]<0.65 and obs['Head'][0] == 0

'''
Devuelve los motores del robot
'''
# def recoverRobotParts(clientID):
# 	#Recover the handles for the motors
# 	LUMRetCode, LUM = vrep.simxGetObjectHandle(clientID, "LUM", vrep.simx_opmode_blocking)
# 	LLMRetCode, LLM = vrep.simxGetObjectHandle(clientID, "LLM", vrep.simx_opmode_blocking)
# 	RUMRetCode, RUM = vrep.simxGetObjectHandle(clientID, "RUM", vrep.simx_opmode_blocking)
# 	RLMRetCode, RLM = vrep.simxGetObjectHandle(clientID, "RLM", vrep.simx_opmode_blocking)
# 	headRetCode, head = vrep.simxGetObjectHandle(clientID, "Head", vrep.simx_opmode_blocking)
# 	return (LUM,LLM,RUM,RLM,head)
'''
Cambia la velocidad de un motor en el simulador
'''
# def setVelocity(clientID, motorHandle, targetVelocity):
# 	vrep.simxSetJointTargetVelocity(clientID, motorHandle, targetVelocity, vrep.simx_opmode_oneshot)

'''
Devuelve la posición de un objeto dentro del simulador
'''
# def getPosition(clientID, objectID):
# 	return vrep.simxGetObjectPosition(clientID, objectID, -1, vrep.simx_opmode_oneshot)


def recoverPorts():
	with open("ports.yml", 'r') as ymlFile:
		portConfig = y.load(ymlFile)
	return portConfig['ports']


class myEnv:
	# portNumb = 19997
	# actions = []
	# hasFallen = False
	# LUM = 0
	# LLM = 0
	# RUM = 0
	# RLM = 0
	# head = 0
	# LUMSpeed = 0
	# LLMSpeed = 0
	# RUMSpeed = 0
	# RLMSpeed = 0
	clientID = -1
	# #1200 es un minuto
	# #600 son 30 segundos
	# maxActions = 600


	
	def __init__(self, max_actions=600):
		self.max_actions = max_actions
		self.portNumb = recoverPorts()[0]
		self.actions = []
		self.score = 0
		self.hasfallen = False
		# self.LUMSpeed = 0
		# self.LLMSpeed = 0 
		# self.RUMSpeed = 0 
		# self.RLMSpeed = 0
		self.clientID = vrep.simxStart('127.0.0.1', self.portNumb, True, True, 5000, 5)
		if self.clientID != -1 :
			print ("Connection to the simulator has been established")
			self.robotController = robotController(self.clientID)

			# LUM,LLM,RUM,RLM,head = recoverRobotParts(self.clientID)
			# self.LUM  = LUM
			# self.LLM = LLM
			# self.RUM = RUM
			# self.RLM = RLM
			# self.head = head
			#Set simulation to be Synchonous instead of Asynchronous
			vrep.simxSynchronous(self.clientID, True)
			#Start simulation if it didn't start
			vrep.simxStartSimulation(self.clientID,vrep.simx_opmode_blocking)
			self.robotController.resetRobot()
			# setVelocity(self.clientID,self.LUM,self.LUMSpeed)
			# setVelocity(self.clientID,self.LLM,self.LLMSpeed)
			# setVelocity(self.clientID,self.RUM,self.RUMSpeed)
			# setVelocity(self.clientID,self.RLM,self.RLMSpeed)
			#Esto es necesario porque la primera observación siempre es incorrecta
			self.observation_space()
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
		observations = self.robotController.observablePositions()
		return sum([v[1] for k,v in observations.items()],[])
		# LUMPos = getPosition(self.clientID,self.LUM)
		# LLMPos = getPosition(self.clientID,self.LLM)
		# RUMPos = getPosition(self.clientID,self.RUM)
		# RLMPos = getPosition(self.clientID,self.RLM)
		# headPos = getPosition(self.clientID, self.head)
		# return [LUMPos[1][0],LUMPos[1][1],LUMPos[1][2],LLMPos[1][0],LLMPos[1][1],LLMPos[1][2],RUMPos[1][0],RUMPos[1][1],RUMPos[1][2],RLMPos[1][0],RLMPos[1][1],RLMPos[1][2],self.LLMSpeed,self.LUMSpeed,self.RLMSpeed,self.RUMSpeed, headPos[1][0],headPos[1][1],headPos[1][2]]

	'''
	Devuelve un array con la lista de acciones posibles en base decimal
	'''
	def action_space(self):
		action_s = []
		numMotors = len(self.robotController.motors)
		print(numMotors)
		num_actions = 3**numMotors
		print(num_actions)
		for i in range(num_actions):
			action_s.append(i)
		return action_s


	'''
	Este método recibe una acción y debería realizarla durante el próximo perído de tiempo de acción

	Retorna 
		- observaciones array dim = 9
		- reward si la acción fue positiva o negativa (diferencia del puntaje con el score)
		- done (si se terminaron la cantidad de acciónes posibles o si el robot se ha caído)
	'''
	def step(self, action):
		action = np.argmax(action)
		codedAction = decimalToOneHot(action,len(self.robotController.motors))
		self.actions.append(action)
		previousObs = self.robotController.observablePositions()
		self.moveRobot(codedAction)
		# self.moveRobot(codedAction)
		obs = self.robotController.observablePositions()
		done = hasFallen(obs) or len(self.actions) > self.max_actions	
		reward = calculateReward(previousObs, obs, len(self.actions))
		# Transform dictionary to list
		obsList = sum([v[1] for k,v in obs.items()],[])
		return (obsList, reward, done)

	def stepWithOutArgMax(self, action):
		codedAction = decimalToOneHot(action,len(self.robotController.motors))
		self.actions.append(action)
		previousObs = self.robotController.observablePositions()
		self.moveRobot(codedAction)
		# self.moveRobot(codedAction)
		obs = self.robotController.observablePositions()
		done = hasFallen(obs) or len(self.actions) > self.max_actions	
		reward = calculateReward(previousObs, obs, len(self.actions))
		# Transform dictionary to list
		obsList = sum([v[1] for k,v in obs.items()],[])
		return (obsList, reward, done)

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
		self.robotController.resetRobot()
		obs = self.robotController.observablePositions()
		obsList = sum([v[1] for k,v in obs.items()],[])
		return obsList

	
	def advanceTime(self):
		vrep.simxSynchronousTrigger(self.clientID)

	def moveRobot(self, codedAction):
		self.robotController.changeMotorsVelocities(codedAction)
		# setVelocity(self.clientID, self.LUM, codedAction[0])
		# setVelocity(self.clientID, self.LLM, codedAction[1])
		# setVelocity(self.clientID, self.RUM, codedAction[2])
		# setVelocity(self.clientID, self.RLM, codedAction[3])
		self.advanceTime()

	def __del__(self):
		vrep.simxStopSimulation(self.clientID,vrep.simx_opmode_blocking)
