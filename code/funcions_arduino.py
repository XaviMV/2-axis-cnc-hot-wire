from Arduino import Arduino
import time as t

# Fitxer per guardar funcions relacionades amb controlar la arduino

class arduino_info:
	def __init__(self):
		# Pins a utilitzar, mirar que els pins dels servos tinguin implementada la funcionalitat pwm
		self.llegir_pins()
		try:
			self.board = iniciar_board(self)
		except:
			self.board = 1

	def llegir_pins(self):
		with open("data/arduino_pins.txt", 'r') as file:
			linies = file.readlines()
			self.PIN_SERVO_1 = int(linies[0])
			self.PIN_SERVO_2 = int(linies[1])

			self.PIN_STEPPER_1_STEP = int(linies[2])
			self.PIN_STEPPER_2_STEP = int(linies[3])

			self.PIN_STEPPER_1_DIR = int(linies[4])
			self.PIN_STEPPER_2_DIR = int(linies[5])



# funcio per moure els sevos amb les pwm donades
def moure_servos(pwm1, pwm2, a):

	a.board.analogWrite(a.PIN_SERVO_1, pwm1)
	a.board.analogWrite(a.PIN_SERVO_2, pwm2)


def moure_steppers(steppers_clicats, stepper1_invertit, stepper2_invertit, a):

	# mirar que nomes es cliqui 1 sol boto
	clicat = -1
	for i in range(len(steppers_clicats)):
		if steppers_clicats[i] == 1:
			if clicat != -1: # si es troba un segon boto clicat es para la funcio
				return
			clicat = i

	if clicat == -1:
		return

	# Segur que hi ha una forma molt millor de tractar les direccions dels steppers si estan invertits pero estic massa cansat com per pensar en com fer-la

	if clicat % 2 == 0: # S'ha clicat alguna fletxa superior (va cap a X = 0)
		if not stepper1_invertit:
			a.board.digitalWrite(a.PIN_STEPPER_1_DIR, "LOW")
		else:
			a.board.digitalWrite(a.PIN_STEPPER_1_DIR, "HIGH")

		if not stepper2_invertit:
			a.board.digitalWrite(a.PIN_STEPPER_2_DIR, "LOW")
		else:
			a.board.digitalWrite(a.PIN_STEPPER_2_DIR, "HIGH")
	else:	# Si ha sigut una fletxa inferior
		if stepper1_invertit:
			board.digitalWrite(a.PIN_STEPPER_1_DIR, "LOW")
		else:
			a.board.digitalWrite(a.PIN_STEPPER_1_DIR, "HIGH")

		if stepper2_invertit:
			a.board.digitalWrite(a.PIN_STEPPER_2_DIR, "LOW")
		else:
			a.board.digitalWrite(a.PIN_STEPPER_2_DIR, "HIGH")


	temps_per_step = 0.01
	iteracions = 1
	if clicat == 2 or clicat == 6: # s'han de fer 20 steps (fletxa gran)
		iteracions = 30
		temps_per_step = 0.004
	
	pin_stepper = 0
	if clicat < 4: # stepper 1
		pin_stepper = a.PIN_STEPPER_1_STEP
	else: # stepper 2
		pin_stepper = a.PIN_STEPPER_2_STEP

	for i in range(iteracions):
		a.board.digitalWrite(pin_stepper, "HIGH")
		t.sleep(0.01)
		a.board.digitalWrite(pin_stepper, "LOW")
		t.sleep(0.01)

def iniciar_board(a):
	board = Arduino("115200")

	board.pinMode(a.PIN_SERVO_1, "OUTPUT")
	board.pinMode(a.PIN_SERVO_2, "OUTPUT")
	board.pinMode(a.PIN_STEPPER_1_STEP, "OUTPUT")
	board.pinMode(a.PIN_STEPPER_2_STEP, "OUTPUT")
	board.pinMode(a.PIN_STEPPER_1_DIR, "OUTPUT")
	board.pinMode(a.PIN_STEPPER_2_DIR, "OUTPUT")

	board.analogWrite(a.PIN_SERVO_1, 128)
	board.analogWrite(a.PIN_SERVO_2, 128)

	# important no deixar els valors dels steppers flotant perque llavors es poden moure sols
	board.digitalWrite(a.PIN_STEPPER_1_STEP, "LOW")
	board.digitalWrite(a.PIN_STEPPER_2_STEP, "LOW")

	board.digitalWrite(a.PIN_STEPPER_1_DIR, "LOW")
	board.digitalWrite(a.PIN_STEPPER_2_DIR, "LOW")

	return board