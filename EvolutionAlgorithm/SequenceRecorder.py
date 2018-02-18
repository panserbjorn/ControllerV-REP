import functools


def recordSequences (newSequences, fileName):
	f = open(fileName, "w")
	halfParsed = list(map( lambda sec: list(map(lambda instr: str(instr[0]) + '-' + str(round(instr[1])),sec)),newSequences))
	fullParsed = list(map(lambda hsec:functools.reduce(lambda b,x:b + ',' + x,hsec),halfParsed))
	for i in fullParsed:
		f.write(i)
		f.write('\n')
	f.close()
	
def readInstructions(fileName):
	instructions = []
	archivo = open(fileName, "r") 
	for line in archivo:
		instructions.append(line)
	archivo.close()
	#Remove ending '\n' from strings
	for i in range(0,len(instructions)):
		instructions[i] = instructions[i].replace('\n', '')
	#Parse lines of instructions to list of list of tuples with motor and velocity
	parsedInstructions = []
	for i in instructions:
		velocitySeries = []
		splitbycomma = i.split(',')
		for j in splitbycomma:
			splitbydash = j.split('-')
			velocitySeries.append((int((splitbydash[0])), int(splitbydash[1])))
		parsedInstructions.append(velocitySeries)
	return parsedInstructions