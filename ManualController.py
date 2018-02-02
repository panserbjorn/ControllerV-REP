#Python code for Manual controller
#Author Joaquín Silveira

import vrep
import time 
import robotConfigDec as rc

'''
This class interacts with the robot through the simulator api (V-REP)
'''
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

	
	def moveRobot(self, action):
		for i in self.movements[action-1]['velocities']:
			self.setVelocity(self.motorsAndHandles[i[0]],i[1])

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
		while stillRun:
			nextAction = input("Write a movement option:   ")
			nextAction = int(nextAction)
			while nextAction:
				robotcontroller.moveRobot(nextAction)
				nextAction = input("Write other movement option or 0   ")
				nextAction = int(nextAction)
			continueRuning = input("want to continue traying? y/n  ")
			if continueRuning == "y":
				stillRun = False
			else:
				#Restart Simulation
				vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
				time.sleep(2)
				vrep.simxStartSimulation(clientID, vrep.simx_opmode_blocking)
		#Finish simulation and connections
		vrep.simxStopSimulation(clientID, vrep.simx_opmode_blocking)
		vrep.simxFinish(clientID)

if __name__ == "__main__":
	main()