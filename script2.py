#Python code for de controller of my thesis
#Author Joaquín Silveira

import vrep 
import time
import numpy as np
import matplotlib.pyplot as plt
import secuenceGenerator as sg

def mainLoop(mode):
	nombreArchivo = ""
	if mode == 'incr':
		print("El programa se ejecutará de la manera tradicional")
		nombreArchivo = "nuevo.txt"
	else: 
		print("El programa se ejecutará para visualizar las mejores corridas")
		nombreArchivo = "nuevo.txt"
	vrep.simxFinish(-1)
	portNumb = 19997
	clientID = vrep.simxStart('127.0.0.1', portNumb, True, True, 5000, 5)
	#clientID = 0
	if clientID != -1 :
		print ("se pudo establecer la conexión con la api del simulador")
		

		#Recover the handles for the motors
		LUMRetCode, LUM = vrep.simxGetObjectHandle(clientID, "LUM", vrep.simx_opmode_blocking)
		LLMRetCode, LLM = vrep.simxGetObjectHandle(clientID, "LLM", vrep.simx_opmode_blocking)
		RUMRetCode, RUM = vrep.simxGetObjectHandle(clientID, "RUM", vrep.simx_opmode_blocking)
		RLMRetCode, RLM = vrep.simxGetObjectHandle(clientID, "RLM", vrep.simx_opmode_blocking)
		#print(LUMRetCode, LUM)
		#print(LLMRetCode, LLM)
		#TODO Debería chequear acá que todos los motores se recuperaron con el código de retorno

		#Recover the handles for other parts of the robot
		HeadRetCode, head = vrep.simxGetObjectHandle(clientID, "Head", vrep.simx_opmode_blocking)

		#Set Initial Target Velocity to 0
		LUMSpeed = 0
		LLMSpeed = 0 
		RUMSpeed = 0 
		RLMSpeed = 0
		vrep.simxSetJointTargetVelocity(clientID, LUM, LUMSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, LLM, LLMSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, RUM, RUMSpeed, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(clientID, RLM, RLMSpeed, vrep.simx_opmode_oneshot)

		


		#Read Instructions from file
		instructions = []
		archivo = open(nombreArchivo, "r") 
		for line in archivo:
			instructions.append(line)
		archivo.close()
		#print(instructions)
		#Remove ending '\n' from strings
		for i in range(0,len(instructions)):
			instructions[i] = instructions[i].replace('\n', '')
		#print(instructions)
		#Parse lines of instructions to list of list of tuples with motor and velocity
		parsedInstructions = []
		for i in instructions:
			velocitySeries = []
			splitbycomma = i.split(',')
			for j in splitbycomma:
				splitbydash = j.split('-')
				velocitySeries.append((int((splitbydash[0])), int(splitbydash[1])))
			parsedInstructions.append(velocitySeries)

		#Set simulation to be Synchonous instead of Asynchronous
		vrep.simxSynchronous(clientID, True)
		#Setting Time Step to 50 ms (miliseconds)
		dt = 0.05
		#Time step should NEVER be set to custom because it messes up the simulation behavior!!!!
		#vrep.simxSetFloatingParameter(clientID, vrep.sim_floatparam_simulation_time_step, dt, vrep.simx_opmode_blocking)
		#Start simulation if it didn't start
		vrep.simxStartSimulation(clientID,vrep.simx_opmode_blocking)

		#This are for controlling where I'm in the instructions while simulation is running
		secuenceIndex = 0
		runInfo = []
		headSecuenceTrace = []
		lowerSpeed, upperSpeed = 0, 0
		secuenceTimes = []
		for secuence in parsedInstructions:
			instructionIndex = 0
			headTrace = []
			extraPoints = 0
			for instruction in secuence:
				instructionIndex+=1
				#This if statement determines which movement the robot sould perform
				if (instruction[0] == 1):
					#Right_contract
					lowerSpeed = -1
					upperSpeed = 1
					vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 2):
					#Right_stretch
					lowerSpeed = 1
					upperSpeed = -1
					vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 3):
					#Right_ahead
					lowerSpeed = 0
					upperSpeed = 1
					vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 4):
					#Right_back
					lowerSpeed = 0
					upperSpeed = -1
					vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 5):
					#Left_contract
					lowerSpeed = -1
					upperSpeed = 1
					vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 6):
					#Left_stretch
					lowerSpeed = 1
					upperSpeed = -1
					vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 7):
					#Left_ahead
					lowerSpeed = 0
					upperSpeed = 1
					vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 8):
					#Left_back
					lowerSpeed = 0
					upperSpeed = -1
					vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 9):
					#Stop_left
					lowerSpeed = 0
					upperSpeed = 0
					vrep.simxSetJointTargetVelocity(clientID, LUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, LLM, lowerSpeed, vrep.simx_opmode_oneshot)
				elif (instruction[0] == 10):
					#Stop_right
					lowerSpeed = 0
					upperSpeed = 0
					vrep.simxSetJointTargetVelocity(clientID, RUM, upperSpeed, vrep.simx_opmode_oneshot)
					vrep.simxSetJointTargetVelocity(clientID, RLM, lowerSpeed, vrep.simx_opmode_oneshot)
				
				#This is what makes the simulation Synchronous
				#initialTime = vrep.simxGetLastCmdTime(clientID)
				#initialTime = 0
				initialTime = 0.0
				#initialTime = 0.4567
				#initialTime = 0.8
				#initialTime = 200000.3243255
				actualTime = initialTime + dt
				#print(initialTime," - ", actualTime," - ", actualTime-initialTime," - ",instruction[1]," - ", instruction[1]/10)
				#Condition to make a new movement
				hasFallen = False
				vrep.simxSynchronousTrigger(clientID)
				#Retrive head position
				headPosition = vrep.simxGetObjectPosition(clientID, head, -1, vrep.simx_opmode_oneshot)
				headTrace.append(headPosition)
				while((actualTime - initialTime) < (instruction[1]/10)):
					#Make de simulation run one step (dt determines how many seconds pass by between step and step)
					vrep.simxSynchronousTrigger(clientID)
					#Retrive head position
					headPosition = vrep.simxGetObjectPosition(clientID, head, -1, vrep.simx_opmode_oneshot)
					headTrace.append(headPosition)
					#Advance time in my internal counter
					actualTime = actualTime + dt
					extraPoints += dt
					if(instructionIndex > 1 and headPosition[0] == 0 and headPosition[1][2]<0.65):
						hasFallen = True
						break
				if(hasFallen):
					break
			print("Secuence: ", secuenceIndex, " has finished")
			print(secuence)
			'''
					TODO 
					Una vez que pueda pedir las posiciones de la cabeza, puedo determinar
					cuando el robot se ha caido.
					Así que puedo pasar a la siguiente secuancia si se cayó.
					Además puedo guardar las posiciones en una lista y cuando terminó 
					la secuancia, guardar la secuencia de posiciones en un archivo.
			'''
			secuenceTimes.append(extraPoints)
			#Here I collect the data for the whole secuence
			headSecuenceTrace.append(list(filter(lambda x: x[0] == 0,headTrace)))
			#TODO Tal vez necesito truncar todos los valores en los cuales la cabeza se haya caido.
			runInfo.append((secuenceIndex,max(list(map(lambda x: x[1][0],list(filter(lambda x: x[0] == 0 and x[1][2] > 0.65,headTrace)))))+extraPoints))
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
		TODO Ahora tengo que ver de raficar por separado cada una de las secuencias 
		y en cada una de ellas poder ver los 3 ejes en lugar de solo el x. 
		así después puedo ver cómo hacer para asignar un valor de resultado
		a cada una de las corridas. El cual va a depender de cómo se movió la cabeza en los 3 ejes.
		'''
		#Visualization of the info collected

		sortedScore = sorted(runInfo, key=lambda x:x[1], reverse=True)
		filteredBestSec = []
		for i in range(0,10):
			filteredBestSec.append(parsedInstructions[sortedScore[i][0]])
		sg.recordSecuences(filteredBestSec, "mejores.txt")
		print(runInfo)
		sg.recordRunOutput(runInfo, "salida.txt")
		if mode == 'incr':
			newLot = []
			for x in filteredBestSec:
				newLot = newLot + sg.generateNewSec(x,10)
			sg.recordSecuences(filteredBestSec + newLot, "nuevo.txt")
		else:
			for h in headSecuenceTrace:
				plt.plot(np.linspace(0,1,len(h)),list(map(lambda x:x[1][0],h)))
				plt.plot(np.linspace(0,1,len(h)),list(map(lambda x:x[1][1],h)))
				plt.plot(np.linspace(0,1,len(h)),list(map(lambda x:x[1][2],h)))
			plt.show()



	else:
		print ("No se pudo establecer conexión con la api del simulador")
		print ("Verificar que el simulador está abierto")

# for x in range(0,15):
# 	print("Vuelta número: ",x)
# 	mainLoop('incr')
mainLoop('visual')