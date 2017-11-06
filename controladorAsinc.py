#Python example code for de controller of my thesis
#Author Joaquín Silveira

import vrep 
import time
'''
Clases que tengo que implementar:
 - Controlador
 - Movimientos
 - Lector de instrucciones
 - Salida del simulador
'''

vrep.simxFinish(-1)
portNumb = 19997
clientID = vrep.simxStart('127.0.0.1', portNumb, True, True, 5000, 5)
#clientID = 0
if clientID != -1 :
	print ("se pudo establecer la conexión con la api del simulador")

	#Start simulation if it didn't start
	vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot)

	#Recover the handles for the motors
	LUMRetCode, LUM = vrep.simxGetObjectHandle(clientID, "LUM", vrep.simx_opmode_blocking)
	LLMRetCode, LLM = vrep.simxGetObjectHandle(clientID, "LLM", vrep.simx_opmode_blocking)
	RUMRetCode, RUM = vrep.simxGetObjectHandle(clientID, "RUM", vrep.simx_opmode_blocking)
	RLMRetCode, RLM = vrep.simxGetObjectHandle(clientID, "RLM", vrep.simx_opmode_blocking)
	print(LUMRetCode, LUM)
	print(LLMRetCode, LLM)
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
	archivo = open("archivo.txt", "r") 
	for line in archivo:
		instructions.append(line)
	archivo.close()
	print(instructions)
	#Remove ending '\n' from strings
	for i in range(0,len(instructions)):
		instructions[i] = instructions[i].replace('\n', '')
	print(instructions)
	#Parse lines of instructions to list of list of tuples with motor and velocity
	parsedInstructions = []
	for i in instructions:
		velocitySeries = []
		splitbycomma = i.split(',')
		for j in splitbycomma:
			splitbydash = j.split('-')
			velocitySeries.append((int((splitbydash[0])), int(splitbydash[1])))
		parsedInstructions.append(velocitySeries)
	lowerSpeed, upperSpeed = 0, 0
	for secuence in parsedInstructions:
		for instruction in secuence:
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
				'''
				TODO Tengo que cambiar el sleep por controlar el tiempo en le simulación
				Entonces voy a hacer un loop infinito en el cual pregunto el tiempo, 
				luego guardo el tiempo y la diferencia entre el t inicial y el actual 
				debe ser igual o mayor que el de la la próxima instrucción. 
				De esa manera entre vuelta y vuelta del while que espera a que 
				pase el tiempo voy a poder preguntar por las posiciones de la 
				cabeza y de otras partes del cuerpo del robot.
				Una vez que pueda pedir las posiciones de la cabeza, puedo determinar
				cuando el robot se ha caido.
				Así que puedo pasar a la siguiente secuancia si se cayó.
				Además puedo guardar las posiciones en una lista y cuando terminó 
				la secuancia, guardar la secuencia de posiciones en un archivo.
				'''
			time.sleep(instruction[1]/10)
		
		#Stop_Start_Simulation
		vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
		time.sleep(2)
		vrep.simxStartSimulation(clientID, vrep.simx_opmode_blocking)
	#Should always end by finishing connetions
	vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
	vrep.simxFinish(clientID)



else:
	print ("No se pudo establecer conexión con la api del simulador")
	print ("Verificar que el simulador está abierto")