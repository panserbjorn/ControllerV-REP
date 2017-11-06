'''
Acá en este archivo voy a hacer un conjunto de funciones 
que lo que hagan es multiplicar las líneas de secuencias del archivo de texto que tengo ahora.
Así que lo que van a lograr es dada una secuencia y un archivo en el cual van a escupir la salida, 
modifican aleatoriamente los tiempos de esa secuencia unas mil veces guardandolas en una lista ignorando 
los repetidos para poder luego guardar en el archivo esas secuencias.

'''

import numpy as np
import functools

def generateNewSec(secuence, numberOfSec):
	newSecuences = []
	while len(newSecuences) < numberOfSec:
		nextSec = []
		for instruct in secuence:
			movement = instruct[0]
			time = instruct[1]
			modification = np.random.randint(-5,5)
			nextSec.append((movement,abs(time+modification)))
		if nextSec not in newSecuences:
			newSecuences.append(nextSec)
	return newSecuences


def recordSecuences (newSecuences, fileName):
	f = open(fileName, "w")
	halfParsed = list(map( lambda sec: list(map(lambda instr: str(instr[0]) + '-' + str(instr[1]),sec)),newSecuences))
	fullParsed = list(map(lambda hsec:functools.reduce(lambda b,x:b + ',' + x,hsec),halfParsed))
	for i in fullParsed:
		f.write(i)
		f.write('\n')
	f.close()
#recordSecuences(generateNewSec([(1,5),(3,5),(2,5),(10,2),(4,2),(8,2),(10,0),(9,0),(5,5),(7,5),(6,5),(9,2),(4,1),(8,1),(10,0),(9,0),(1,5),(3,6),(2,5),(10,2),(5,5),(7,5),(6,5),(9,2),(4,2),(8,2),(10,0),(9,0),(1,5),(3,5),(2,5),(10,2)],20),"newFile.txt ")

def recordRunOutput(runInfo, fileName):
	f = open(fileName, "w")
	for i in runInfo:
		f.write(str(i[0]) + "," + str(i[1]))
		f.write('\n')
	f.close()

def func():
	return 4