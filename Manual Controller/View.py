#Code for viewing saved secuences
#Author Joaquín Silveira

import vrep 
import time
import argparse
import robotConfigDec as rc
from ManualController import robotController

def readInstructions(fileName):
	instructions = []
	file = open(fileName, "r") 
	for line in file:
		instructions.append(line)
	file.close()
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

def main(fileName):
	#Maing sure no connection is active
	vrep.simxFinish(-1)
	#Default Port Numeber
	portNumb = 19997
	#Establish connection
	clientID = vrep.simxStart('127.0.0.1', portNumb, True, True, 5000, 5)
	#Verify connection
	if clientID == -1 :
		print("Connection to the simluator api could not be established")
		print("Make sure the simulator is up and running on port 19997")
	else:
		parsedInstructions = readInstructions(fileName)

		#Set simulation to be Synchonous instead of Asynchronous
		vrep.simxSynchronous(clientID, True)

		#Start simulation
		vrep.simxStartSimulation(clientID, vrep.simx_opmode_oneshot)
		robotcontroller = robotController(clientID)
		print(parsedInstructions)
		for secuence in parsedInstructions:
			for instruction in secuence:
				robotcontroller.moveRobot(instruction[0])
				for i in range(instruction[1]):
					vrep.simxSynchronousTrigger(clientID)

			#Stop_Start_Simulation
			vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
			#This sleep is necesary for the simulation to finish stopping before starting again
			time.sleep(2)
			vrep.simxStartSimulation(clientID, vrep.simx_opmode_blocking)
		#Should always end by finishing connetions
		vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
		vrep.simxFinish(clientID)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='View saved secuences of manual contorller ')
	parser.add_argument('fileName', type=str, help='File name where secuences are stored,')
	args = parser.parse_args()
	main(**vars(args))