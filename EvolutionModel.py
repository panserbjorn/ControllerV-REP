#Python code for de evolution model
#Author Joaquín Silveira

import vrep
import time 
import robotConfigDec as rc
import functools
import numpy as np
import math
from multiprocessing.pool import ThreadPool
import secuenceGenerator as sg
import argparse


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

#TODO Cambiar estos metodos para otro lugar ( no debería ser responsabilidad de este módulo )
def recordSecuences (newSecuences, fileName):
	f = open(fileName, "w")
	halfParsed = list(map( lambda sec: list(map(lambda instr: str(instr[0]) + '-' + str(round(instr[1])),sec)),newSecuences))
	fullParsed = list(map(lambda hsec:functools.reduce(lambda b,x:b + ',' + x,hsec),halfParsed))
	for i in fullParsed:
		f.write(i)
		f.write('\n')
	f.close()

def readInstructions(fileName):
	instructions = []
	archivo = open(fileName, "r") 
	for line in archivo:
		instructions.append(line)
	archivo.close()
	#Remove ending '\n' from strings
	for i in range(0,len(instructions)):
		instructions[i] = instructions[i].replace('\n', '')
	#Parse lines of instructions to list of list of tuples with motor and velocity
	parsedInstructions = []
	for i in instructions:
		velocitySeries = []
		splitbycomma = i.split(',')
		for j in splitbycomma:
			splitbydash = j.split('-')
			velocitySeries.append((int((splitbydash[0])), int(splitbydash[1])))
		parsedInstructions.append(velocitySeries)
	return parsedInstructions

'''
This class interacts with the robot through the simulator api (V-REP)
'''
#TODO Mover el controlador del robot a un archivo aparte para que todas las clases lo puedan usar
class robotController:

	def getPosition(self, objectHandle):
		return vrep.simxGetObjectPosition(self.clientID, objectHandle, -1, vrep.simx_opmode_oneshot)

	def getObjectHandle(self, objectName):
		retCode, handle = vrep.simxGetObjectHandle(self.clientID, objectName, vrep.simx_opmode_blocking)
		return handle

	def setVelocity(self, handle, velocity):
		vrep.simxSetJointTargetVelocity(self.clientID, handle, velocity, vrep.simx_opmode_oneshot)

	def __init__(self, clientID):
		self.clientID = clientID
		#Recover the handles for the motors
		self.motors, self.observables = rc.getRobotConfig()
		self.movements = rc.getRobotMovements()
		self.motorsAndHandles = {i : self.getObjectHandle(i) for i in self.motors}
		
		
		#Recover the handles for other parts of the robot
		self.observablesAndHandles = {i : self.getObjectHandle(i) for i in self.observables}

		#Set Initial Target Velocity of all motors to 0
		for k, v in self.motorsAndHandles.items():
			self.setVelocity(v,0)


	def observablePositions(self):
		return {k : self.getPosition(v) for k,v in self.observablesAndHandles.items()}

	def resetRobot(self):
		for k,v in self.motorsAndHandles.items():
			self.setVelocity(v,0)

	def moveRobot(self, action):
		for i in self.movements[action-1]['velocities']:
			self.setVelocity(self.motorsAndHandles[i[0]],i[1])

'''
This class gives de score for every run in the evolution model, 
based in the observations
'''
#TODO mover esta clase a un archivo aparte para que otro pueda implementarla
class EvolutionModel():
	#TODO implementar esta clase
	#This determines if the robot has fallen
	def isDone(self, observations):
		return observations['Head'][0] == 0 and observations['Head'][1][2] < 0.65

	def distancia(self, puntoA, puntoB):
		return abs(puntoA[0]-puntoB[0])+ abs(puntoA[2]-puntoB[2])

	def puntoMovil(self, tiempo):
		return ((tiempo*0.09)-1.5,0.03,0.8)


	def getScore(self, observationTrace):
		#Filter not valid positions
		observationTrace = list(filter(lambda x: x['Observation']['Head'][0] == 0,observationTrace))
		return sum(map(lambda x:math.log(1/self.distancia(x['Observation']['Head'][1],self.puntoMovil(x['runtime']))),observationTrace))

def recoverPorts():
	return [19997]

def main(sec_file, best_file, numb_threads, exploration_factor, num_gen):
	#Maing sure no connection is active
	vrep.simxFinish(-1)
	#Recover port numbers
	ports = recoverPorts()
	pool = ThreadPool(numb_threads)
	for gen in range(num_gen):
		instructions = readInstructions(sec_file)
		instructionChunks = list(chunks(instructions, math.floor(len(instructions)/numb_threads)))
		runInfo = []
		for i in range(numb_threads):
			runInfo.append(pool.apply_async(runModel, args=(ports[i], instructionChunks[i])))
		pool.close()
		pool.join()
		runInfo = [r.get() for r in runInfo]
		runInfo2 = []
		for i in runInfo:
			runInfo2 += i
		#TODO cambiar 1 por palabra en diccionario
		#Sort by score
		#print(runInfo[0])
		sortedByScore = sorted(runInfo2, key=lambda x:x['Score'],reverse=True)
		bestSecuences = [r['instructions'] for r in sortedByScore[:10]]
		newSecuences = [sg.generateNewSec(sec, exploration_factor) for sec in bestSecuences]
		newSecuences = sum(newSecuences,[])
		recordSecuences(bestSecuences + newSecuences, sec_file)
		recordSecuences(bestSecuences, best_file)

def runModel(portNumber, secuenceList):
	#Establish connection
	clientID = vrep.simxStart('127.0.0.1', portNumber, True, True, 5000, 5)
	#Verify connection
	if clientID == -1 :
		print("Connection to the simluator api could not be established")
		print("Make sure the simulator is up and running on port {}".format(portNumber))
	else:
		evolutionModel = EvolutionModel()
		robotcontroller = robotController(clientID)
		#Set simulation to be Synchronous instead of Asynchronous
		vrep.simxSynchronous(clientID, True)
		
		#Setting Time Step to 50 ms (miliseconds)
		dt = 0.05
		#Start simulation
		vrep.simxStartSimulation(clientID, vrep.simx_opmode_oneshot)
		runInfo = []
		for secuence in secuenceList:
			runtime = 0
			observationTrace = []
			for instruction in secuence:
				robotcontroller.moveRobot(instruction[0])

				#This is what makes the simulation Synchronous
				initialTime = 0.0
				actualTime = initialTime + dt
				runtime += dt
				#Condition to stop simulation
				done = False
				vrep.simxSynchronousTrigger(clientID)
				#TODO verificar si esto es necesario
				# observations = robotcontroller.observablePositions()
				#TODO cambiar esto porque la cantidad de veces esté en el archivo ya
				n = 1
				while (n <= instruction[1] and not done): 
					n+=1
					# while ((actualTime - initialTime) < instruction[1] and not done):
					#Make de simulation run one step (dt determines how many seconds pass by between step and step)
					vrep.simxSynchronousTrigger(clientID)
					#Advance time in my internal counter
					actualTime = actualTime + dt
					runtime += dt
					observations = robotcontroller.observablePositions()
					observationTrace.append({'Observation': observations, 'runtime' : runtime})
					done = evolutionModel.isDone(observations)

			runInfo.append({'instructions' : secuence, 'observations' : observationTrace, 'Score' : evolutionModel.getScore(observationTrace)})
			robotcontroller.resetRobot()
			#Stop_Start_Simulation
			vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
			#This sleep is necesary for the simulation to finish stopping before starting again
			time.sleep(2)
			robotcontroller.resetRobot()
			vrep.simxStartSimulation(clientID, vrep.simx_opmode_blocking)
			robotcontroller.resetRobot()
		#Should always end by finishing connetions
		vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
		vrep.simxFinish(clientID)

		return runInfo



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Evolution Model for robots')
	parser.add_argument( '-sf','--sec_file', type=str, help='File Name where secuences are stored', default='secuenceFile.txt')
	parser.add_argument('-bf', '--best_file', type=str, help='File Name where bes secuences are stored', default='bestSecuences.txt')
	parser.add_argument('-th', '--numb_threads', type=int, help='Number of threads to be run', default=4)
	parser.add_argument('-ef', '--exploration_factor', type=int, help='How many new secuences for every old secuence', default=10)
	parser.add_argument('-g', '--num_gen', type=int, help='Number of generations to be run', default=50)
	args = parser.parse_args()
	main(**vars(args))