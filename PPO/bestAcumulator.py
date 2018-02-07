#Python code for Snoop of PPO
#Author Joaquín Silveira

import yaml as y
import ruamel.yaml
import time 
import sys

class BestAcumulator:
	def __init__(self):
		self.sequences = []

	def next_actions(self, newSec):
		self.sequences.append(newSec)
		newSequences = sorted(self.sequences, key=lambda pair: pair['reward'])
		self.sequences = newSequences[:10]



	def save(self, pathFolder):
		# print(self.sequences)
		stream = open("{}/bestSecs.yml".format(pathFolder), 'w')
		# self.sequences = [{'actions': list(i['actions']), 'reward':float(i['reward'])} for i in self.sequences]
		# data = dict(Best=self.sequences)
		# yaml_str = ruamel.yaml.dump(data, stream, default_flow_style=False)
		# ruamel.yaml.round_trip_dump(data, sys.stdout)
		y.dump(self.sequences, stream)
		stream.close()
		# data = ruamel.yaml.load(yaml_str)
		# print(data)
		# ruamel.yaml.round_trip_dump(data, stream)


		