
class myEnv():
	portNumb
	logFileName
	actions
	score
	hasfallen

	'''
	TOOD debería conectarme con el simulador en el init
	Así de esta manera puedo controlar las cosas y poder devolver lo que hacen los otro métodos
	
	'''
	def _init_():
		self.portNumb = 19997
		actions = []
		score = 0
		hasfallen = False

	'''
	Este método debería devolver las posiciones y las velocidades de las partes del robot, no la cantidad de variables a devolver

	'''
	def observation_space():
		#Son las 4 posiciones, más las 4 velocidades de los motores
		#Más la posición de la cabez y la velocidad de la cabeza en el eje x
		return 10

	'''
	Este método debería devolver las acciones posibles en lugar de solo la cantidad de acciones que se pueden realizar
	'''
	def action_space():
		#Son las 64 configuraciones que pueden tener los motres (son 4 motores y 3 estados [apagado, encendido positivo, encendido negativo], así que es 4^3)
		#return 4^3
		return range(4^3)


	'''
	Este método recibe ua acción y debería realizarla durante el próximo perído de tiempo de acción

	Retorna 
		- observaciones array dim = 10
		- reward si la acción fue positiva o negativa (diferencia del puntaje con el score)
		- done (si se terminaron la cantidad de acciónes posibles o si el robot se ha caído)
	'''
	def step(action):
		return 0





