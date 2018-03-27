#Python code for Snoop of manual secuences
#Author Joaquín Silveira

import time 

class Snoop:
	def __init__(self):
		self.sec = []

	def next_action(self, action):
		self.sec.append((action,int(round(time.time()*1000))))

	def end(self):
		finaltime = int(round(time.time()*1000))
		for i in range(len(self.sec)-1):
			self.sec[i] = (self.sec[i][0], self.sec[i+1][1] - self.sec[i][1])
		self.sec[-1] = (self.sec[-1][0], finaltime - self.sec[-1][1])
		parsedSec = [(i[0], i[1]/50) for i in self.sec]
		self.sec = []
		return parsedSec

		