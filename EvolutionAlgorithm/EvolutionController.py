#Python code for de evolution model
#Author Joaquín Silveira

import vrep
import time 
from RobotController import robotController
import functools
import numpy as np
import math
from multiprocessing.pool import ThreadPool
import sequenceGenerator as sg
import argparse
import SequenceRecorder as sr
from EvolutionModel import EvolutionModel
import yaml as y


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]



def recoverPorts():
	with open("evolutionModelPorts.yml", 'r') as ymlFile:
		portConfig = y.load(ymlFile)
	return portConfig['ports']

def main(seq_file, best_file, numb_threads, exploration_factor, num_gen):
	#Maing sure no connection is active
	vrep.simxFinish(-1)
	#Recover port numbers
	ports = recoverPorts()
	pool = ThreadPool(numb_threads)
	for gen in range(num_gen):
		instructions = sr.readInstructions(seq_file)
		instructionChunks = list(chunks(instructions, math.floor(len(instructions)/numb_threads)))
		runInfo = []
		for i in range(numb_threads):
			runInfo.append(pool.apply_async(runModel, args=(int(ports[i]), instructionChunks[i])))
		pool.close()
		pool.join()
		runInfo = [r.get() for r in runInfo]
		runInfo2 = []
		for i in runInfo:
			runInfo2 += i
		#Sort by score
		sortedByScore = sorted(runInfo2, key=lambda x:x['Score'],reverse=True)
		bestSequences = [r['instructions'] for r in sortedByScore[:10]]
		newSequences = [sg.generateNewSeq(seq, exploration_factor) for seq in bestSequences]
		newSequences = sum(newSequences,[])
		sr.recordSequences(bestSequences + newSequences, seq_file)
		sr.recordSequences(bestSequences, best_file)

def runModel(portNumber, sequenceList):
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
		for sequence in sequenceList:
			runtime = 0
			observationTrace = []
			for instruction in sequence:
				robotcontroller.moveRobot(instruction[0])

				#This is what makes the simulation Synchronous
				initialTime = 0.0
				actualTime = initialTime + dt
				runtime += dt
				#Condition to stop simulation
				done = False
				vrep.simxSynchronousTrigger(clientID)
				n = 1
				while (n <= instruction[1] and not done): 
					n+=1
					#Make de simulation run one step (dt determines how many seconds pass by between step and step)
					vrep.simxSynchronousTrigger(clientID)
					#Advance time in my internal counter
					actualTime = actualTime + dt
					runtime += dt
					observations = robotcontroller.observablePositions()
					observationTrace.append({'Observation': observations, 'runtime' : runtime})
					done = evolutionModel.isDone(observations)

			runInfo.append({'instructions' : sequence, 'observations' : observationTrace, 'Score' : evolutionModel.getScore(observationTrace)})
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
	parser.add_argument( '-sf','--seq_file', type=str, help='File Name where sequences are stored', default='sequenceFile.txt')
	parser.add_argument('-bf', '--best_file', type=str, help='File Name where bes sequences are stored', default='bestSequences.txt')
	parser.add_argument('-th', '--numb_threads', type=int, help='Number of threads to be run', default=1)
	parser.add_argument('-ef', '--exploration_factor', type=int, help='How many new sequences for every old sequence', default=10)
	parser.add_argument('-g', '--num_gen', type=int, help='Number of generations to be run', default=50)
	args = parser.parse_args()
	main(**vars(args))