#Python code for robot configuration
#Author Joaquín Silveira
import yaml as y



robotConfigFile = "robotConfig.yml"
movementConfigFile = "movementConfig.yml"


def getRobotConfig():
	with open(robotConfigFile, 'r') as ymlFile:
		robotConfig = y.load(ymlFile)
	return robotConfig['motors'], robotConfig['observables']
def getRobotMovements():
	with open(movementConfigFile, 'r') as ymlFile:
		movementConfig = y.load(ymlFile)
	return movementConfig['movements']


