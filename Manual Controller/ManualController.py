#Python code for Manual controller
#Author Joaquín Silveira

import vrep
import time 
import robotConfigDec as rc
from ManualCtrSnoop import Snoop 
import functools
from RobotController import robotController
import SecuenceRecorder as sr



def main():
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
		#Start simulation
		vrep.simxStartSimulation(clientID, vrep.simx_opmode_oneshot)
		robotcontroller = robotController(clientID)
		print("Write 0 to stop simulation or a number between 1 and {} to move the robot:  ".format(len(robotcontroller.movements)))
		print([(i+1,v['name']) for i,v in enumerate(robotcontroller.movements)])
		stillRun = True
		snoop = Snoop()
		savedSecuences = []
		while stillRun:
			nextAction = input("Write a movement option:   ")
			try:
				nextAction = int(nextAction)
			except:
				nextAction = -1
			while nextAction:
				if robotcontroller.isValid(nextAction):
					snoop.next_action(nextAction)
					robotcontroller.moveRobot(nextAction)
				nextAction = input("Write other movement option or 0   ")
				nextAction = int(nextAction)
			secuence = snoop.end()
			# print(secuence)
			saveRun = input("Do you want to save this run? y/n ")
			if saveRun == "y":
				savedSecuences.append(secuence)
			continueRuning = input("Want to continue traying? y/n  ")
			if continueRuning == "n":
				stillRun = False
			else:
				#Restart Simulation
				vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
				time.sleep(2)
				vrep.simxStartSimulation(clientID, vrep.simx_opmode_blocking)
		#Finish simulation and connections
		vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
		vrep.simxFinish(clientID)
		#Save Secuences into file
		sr.recordSecuences(savedSecuences, "savedSecuences.txt")

if __name__ == "__main__":
	main()