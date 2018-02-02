#Python code for Manual controller
#Author Joaquín Silveira

import vrep
import time 
import robotConfigDec as rc

'''
This class interacts with the robot through the simulator api (V-REP)
'''
class robotController:

	# LUM, LLM, RUM, RLM = 0,0,0,0
	# LUMSpeed, LLMSpeed, RUMSpeed, RLMSpeed = 0,0,0,0
	# Head = 0
	# clientID = -1

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
		# print(self.movements)
		# LUMRetCode, self.LUM = vrep.simxGetObjectHandle(self.clientID, "LUM", vrep.simx_opmode_blocking)
		# LLMRetCode, self.LLM = vrep.simxGetObjectHandle(self.clientID, "LLM", vrep.simx_opmode_blocking)
		# RUMRetCode, self.RUM = vrep.simxGetObjectHandle(self.clientID, "RUM", vrep.simx_opmode_blocking)
		# RLMRetCode, self.RLM = vrep.simxGetObjectHandle(self.clientID, "RLM", vrep.simx_opmode_blocking)
		
		#Recover the handles for other parts of the robot
		HeadRetCode, self.Head = vrep.simxGetObjectHandle(self.clientID, "Head", vrep.simx_opmode_blocking)

		#Set Initial Target Velocity of all motors to 0
		for k, v in self.motorsAndHandles.items():
			self.setVelocity(v,0)
		# vrep.simxSetJointTargetVelocity(self.clientID, self.LUM, self.LUMSpeed, vrep.simx_opmode_oneshot)
		# vrep.simxSetJointTargetVelocity(self.clientID, self.LLM, self.LLMSpeed, vrep.simx_opmode_oneshot)
		# vrep.simxSetJointTargetVelocity(self.clientID, self.RUM, self.RUMSpeed, vrep.simx_opmode_oneshot)
		# vrep.simxSetJointTargetVelocity(self.clientID, self.RLM, self.RLMSpeed, vrep.simx_opmode_oneshot)


	def head_position():
		return vrep.simxGetObjectPosition(self.clientID, self.Head, -1, vrep.simx_opmode_oneshot)

	# def Right_contract(self):
	# 	lowerSpeed = -1
	# 	upperSpeed = 1
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Right_stretch(self):
	# 	lowerSpeed = 1
	# 	upperSpeed = -1
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Right_ahead(self):
	# 	lowerSpeed = 0
	# 	upperSpeed = 1
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Right_back(self):
	# 	lowerSpeed = 0
	# 	upperSpeed = -1
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Left_contract(self):
	# 	lowerSpeed = -1
	# 	upperSpeed = 1
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Left_stretch(self):
	# 	lowerSpeed = 1
	# 	upperSpeed = -1
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Left_ahead(self):
	# 	lowerSpeed = 0
	# 	upperSpeed = 1
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Left_back(self):
	# 	lowerSpeed = 0
	# 	upperSpeed = -1
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Left_stop(self):
	# 	lowerSpeed = 0
	# 	upperSpeed = 0
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.LLM, lowerSpeed, vrep.simx_opmode_oneshot)

	# def Right_stop(self):
	# 	lowerSpeed = 0
	# 	upperSpeed = 0
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RUM, upperSpeed, vrep.simx_opmode_oneshot)
	# 	vrep.simxSetJointTargetVelocity(self.clientID, self.RLM, lowerSpeed, vrep.simx_opmode_oneshot)
	# #This is necessary for the robot movement	
	# movement_options = {
	# 		1 : Right_contract,
	# 		2 : Right_stretch,
	# 		3 : Right_ahead,
	# 		4 : Right_back,
	# 		5 : Left_contract,
	# 		6 : Left_stretch,
	# 		7 : Left_ahead,
	# 		8 : Left_back,
	# 		9 : Left_stop,
	# 		10 : Right_stop
	# }
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