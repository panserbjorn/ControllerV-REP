#Python code for de controller of my thesis
#Author Joaquín Silveira

import vrep 
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import secuenceGenerator as sg

#Funciones auxiliares:
def recoverRobotParts(clientID):
	#Recover the handles for the motors
	LUMRetCode, LUM = vrep.simxGetObjectHandle(clientID, "LUM", vrep.simx_opmode_blocking)
	LLMRetCode, LLM = vrep.simxGetObjectHandle(clientID, "LLM", vrep.simx_opmode_blocking)
	RUMRetCode, RUM = vrep.simxGetObjectHandle(clientID, "RUM", vrep.simx_opmode_blocking)
	RLMRetCode, RLM = vrep.simxGetObjectHandle(clientID, "RLM", vrep.simx_opmode_blocking)

	#Recover the handles for other parts of the robot
	HeadRetCode, head = vrep.simxGetObjectHandle(clientID, "Head", vrep.simx_opmode_blocking)
	return (LUM,LLM,RUM,RLM,head)

def setVelocity(clientID, motorHandle, targetVelocity):
	vrep.simxSetJointTargetVelocity(clientID, motorHandle, targetVelocity, vrep.simx_opmode_oneshot)

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

def moveRobot(clientID, robotMovement, LUM, LLM, RUM, RLM):
	#This if statement determines which movement the robot sould perform
	if (robotMovement == 1):
		#Right_contract
		lowerSpeed = -1
		upperSpeed = 1
		vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 2):
		#Right_stretch
		lowerSpeed = 1
		upperSpeed = -1
		vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 3):
		#Right_ahead
		lowerSpeed = 0
		upperSpeed = 1
		vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 4):
		#Right_back
		lowerSpeed = 0
		upperSpeed = -1
		vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 5):
		#Left_contract
		lowerSpeed = -1
		upperSpeed = 1
		vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 6):
		#Left_stretch
		lowerSpeed = 1
		upperSpeed = -1
		vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 7):
		#Left_ahead
		lowerSpeed = 0
		upperSpeed = 1
		vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 8):
		#Left_back
		lowerSpeed = 0
		upperSpeed = -1
		vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 9):
		#Stop_left
		lowerSpeed = 0
		upperSpeed = 0
		vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
	elif (robotMovement == 10):
		#Stop_right
		lowerSpeed = 0
		upperSpeed = 0
		vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)

def distancia(puntoA, puntoB):
	return abs(puntoA[0]-puntoB[0])+ abs(puntoA[2]-puntoB[2])

def puntoMovil(tiempo):
	return ((tiempo*0.088)-1.5,0.03,0.8)

#Código del controlador
'''
TODO Debería mejorar el modo de ejecución por parámetros por consola
TODO Debería agregar un modo más solo para ver las corridas que se encuentran en archivo.txt, porque muchas veces estoy viendo esas para compararlas con las generadas.
'''
def mainLoop(mode):
	nombreArchivo = ""
	if mode == 'incr':
		print("El programa se ejecutará de la manera tradicional")
		nombreArchivo = "nuevo.txt"
	else: 
		print("El programa se ejecutará para visualizar las mejores corridas")
		nombreArchivo = "archivo.txt"
	vrep.simxFinish(-1)
	portNumb = 19997
	clientID = vrep.simxStart('127.0.0.1', portNumb, True, True, 5000, 5)
	if clientID != -1 :
		print ("se pudo establecer la conexión con la api del simulador")
		
		#Recover handlers for robot parts
		LUM,LLM,RUM,RLM,head = recoverRobotParts(clientID)

		#Set Initial Target Velocity to 0
		LUMSpeed = 0
		LLMSpeed = 0 
		RUMSpeed = 0 
		RLMSpeed = 0
		setVelocity(clientID,LUM,LUMSpeed)
		setVelocity(clientID,LLM,LLMSpeed)
		setVelocity(clientID,RUM,RUMSpeed)
		setVelocity(clientID,RLM,RLMSpeed)

		#Read Instructions from file
		instructions = readInstructions(nombreArchivo)
		
		#Set simulation to be Synchonous instead of Asynchronous
		vrep.simxSynchronous(clientID, True)
		
		#Setting Time Step to 50 ms (miliseconds)
		dt = 0.05
		#WARNING!!! - Time step should NEVER be set to custom because it messes up the simulation behavior!!!!
		#vrep.simxSetFloatingParameter(clientID, vrep.sim_floatparam_simulation_time_step, dt, vrep.simx_opmode_blocking)

		#Start simulation if it didn't start
		vrep.simxStartSimulation(clientID,vrep.simx_opmode_blocking)

		#This are for controlling where I'm in the instructions while simulation is running
		secuenceIndex = 0
		runInfo = []
		headSecuenceTrace = []
		lowerSpeed, upperSpeed = 0, 0
		secuenceTimes = []
		for secuence in instructions:
			instructionIndex = 0
			headTrace = []
			extraPoints = 0
			runtime = 0
			for instruction in secuence:
				instructionIndex+=1
				
				moveRobot(clientID,instruction[0], LUM, LLM, RUM, RLM)
				
				#This is what makes the simulation Synchronous
				initialTime = 0.0
				actualTime = initialTime + dt
				runtime += dt
				#Condition to stop simulation
				hasFallen = False
				vrep.simxSynchronousTrigger(clientID)

				#Retrive head position
				headPosition = vrep.simxGetObjectPosition(clientID, head, -1, vrep.simx_opmode_oneshot)
				#headTrace.append((headPosition,runtime))
				while((actualTime - initialTime) < (instruction[1]/10)):
					#Make de simulation run one step (dt determines how many seconds pass by between step and step)
					vrep.simxSynchronousTrigger(clientID)
					#Advance time in my internal counter
					actualTime = actualTime + dt
					runtime += dt
					#TODO do I still need the extra points for time?
					extraPoints += dt
					#Retrive head position
					headPosition = vrep.simxGetObjectPosition(clientID, head, -1, vrep.simx_opmode_oneshot)
					headTrace.append((headPosition,runtime))
					
					#Verify that the model hasn't fallen
					if(headPosition[0] == 0 and headPosition[1][2]<0.65):
						print("Posición de la cabeza:", headPosition[1][2])
						print("tiempo: ", runtime)
						hasFallen = True
						break
				if(hasFallen):
					break
			if (hasFallen):
				print ("Secuence: ", secuenceIndex, " has fallen!!")
			else:
				print("Secuence: ", secuenceIndex, " has finished without falling")
			print(secuence)
			
			secuenceTimes.append(extraPoints)
		#Here I collect the data for the whole secuence
			#filter not valid positions
			headTrace = list(filter(lambda x: x[0][0] == 0,headTrace))
			#add to whole run trace info
			headSecuenceTrace.append(headTrace)

			fallenFactor = 0
			if hasFallen:
				fallenFactor = -50
			#format: (index, score, headtrace((valid,(x,y,z),time))
			runInfo.append((secuenceIndex, sum(map(lambda x:math.log(1/distancia(x[0][1],puntoMovil(x[1]))),headTrace))+fallenFactor,headTrace))
			print("puntaje obtenido",runInfo[-1][1])
			secuenceIndex+=1
			#Stop_Start_Simulation
			vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
			#This sleep is necesary for the simulation to finish stopping before starting again
			time.sleep(2)
			vrep.simxStartSimulation(clientID, vrep.simx_opmode_blocking)
		#Should always end by finishing connetions
		vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
		vrep.simxFinish(clientID)
		
		
		'''
		TODO Ahora tengo que graficar la posición x de la cabez en las mejores 10 corridas y también el punto móvil 
		'''
		#Visualization of the info collected

		sortedScore = sorted(runInfo, key=lambda x:x[1], reverse=True)
		filteredBestSec = []
		for i in range(0,10):
			filteredBestSec.append(instructions[sortedScore[i][0]])
		sg.recordSecuences(filteredBestSec, "mejores.txt")
		# print(runInfo)
		sg.recordRunOutput(runInfo, "salida.txt")
		if mode == 'incr':
			newLot = []
			for x in filteredBestSec:
				newLot = newLot + sg.generateNewSec(x,10)
			sg.recordSecuences(filteredBestSec + newLot, "nuevo.txt")
		else:
			# TODO graficar solo las mejores 10 y el punto móvil. 
			for h in range(0,10):
				# print ("esto debería ser el tiempo: ", sortedScore[h][2][0])
				# print ("Que es esto?: ", sortedScore[h][0], " ----  ", sortedScore[h][1])
				# # print ("esto debería ser el valor de x: ", sortedScore[h][2][0][1])

				# print (list(map(lambda x:x[2][1],sortedScore[h])))
				# print (list(map(lambda x:x[2][0][1][0],sortedScore[h])))
				plt.plot(list(map(lambda x:x[1],sortedScore[h][2])),list(map(lambda x:x[0][1][0],sortedScore[h][2])))

				#plt.plot(list(map(lambda x:x[1],h)),list(map(lambda x:x[0][1][1],sortedScore[h])))
				#plt.plot(list(map(lambda x:x[1],h)),list(map(lambda x:x[0][1][2],sortedScore[h])))
				timeList = list(map(lambda x:x[1],sortedScore[0][2]))
			plt.plot(timeList,list(map(lambda x: puntoMovil(x)[0],timeList)))
			plt.show()



	else:
		print ("No se pudo establecer conexión con la api del simulador")
		print ("Verificar que el simulador está abierto")

# for x in range(0,25):
# 	print("Vuelta número: ",x)
# 	mainLoop('incr')
mainLoop('visual')


