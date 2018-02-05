import math
import functools


'''
This class gives de score for every run in the evolution model, 
based in the observations
'''
class EvolutionModel():
	#This determines if the robot has fallen
	def isDone(self, observations):
		return observations['Head'][0] == 0 and observations['Head'][1][2] < 0.65

	def distancia(self, puntoA, puntoB):
		return abs(puntoA[0]-puntoB[0])+ abs(puntoA[2]-puntoB[2])

	def puntoMovil(self, tiempo):
		return ((tiempo*0.09)-1.5,0.03,0.8)


	def getScore(self, observationTrace):
		#Filter not valid positions
		observationTrace = list(filter(lambda x: x['Observation']['Head'][0] == 0,observationTrace))
		return sum(map(lambda x:math.log(1/self.distancia(x['Observation']['Head'][1],self.puntoMovil(x['runtime']))),observationTrace))