import vrep
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

	def isValid(self, action):
		return action <= len(self.movements)

	def observablePositions(self):
		return {k : self.getPosition(v) for k,v in self.observablesAndHandles.items()}

	def resetRobot(self):
		for k,v in self.motorsAndHandles.items():
			self.setVelocity(v,0)

	def moveRobot(self, action):
		for i in self.movements[action-1]['velocities']:
			self.setVelocity(self.motorsAndHandles[i[0]],i[1])
