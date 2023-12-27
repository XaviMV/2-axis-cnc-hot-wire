import math
import time as t
from Arduino import Arduino
from funcions_arduino import arduino_info

# POSICIO DEL ORIGEN: el punt (0, 0) esta amb la x al cap de la maquina i la y en la posicio mes baixa

# Posicio minima i maxima dels servos
SERVO_Y_MIN = 0
SERVO_Y_MAX = 5

# Pins a utilitzar, mirar que els pins dels servos tinguin implementada la funcionalitat pwm
PIN_SERVO_1 = 9
PIN_SERVO_2 = 10

PIN_STEPPER_1_STEP = 7
PIN_STEPPER_2_STEP = 8

PIN_STEPPER_1_DIR = 5
PIN_STEPPER_2_DIR = 6


# retorna el valor_obj proporcional al valor_ref, fa el mateix que la funcio "map" en la arduino
def valor_proporcional(valor_ref, valor_ref_min, valor_ref_max, valor_obj_min, valor_obj_max):

	rang_antic = (valor_ref_max - valor_ref_min)  
	rang_nou = (valor_obj_max - valor_obj_min)  
	valor_obj = (((valor_ref - valor_ref_min) * rang_nou) / rang_antic) + valor_obj_min

	return valor_obj


# INPUT:
# x_ini, y_ini -> punt on es troba la cnc abans d'entrar a la funcio
# x_fi, y_fi -> punt objectiu a on es vol portar la cnc
# vel -> velocitat amb la que es vol anar, en cm/s
# servo_info -> llista amb informacio sobre el servo
def anar_a_punt(x_ini, y_ini, x_fi, y_fi, vel, servo_info, stepper1_invertit, stepper2_invertit, a):

	servo1_pwm_min, servo1_pwm_max, servo2_pwm_min, servo2_pwm_max, servo_y_min, servo_y_max = servo_info # servo_y_min hauria de ser sempre 0. Pwm min es refereix a la pwm a la altura minima, pwm max a la maxima, per tant pwm_min pot ser mes gran que pwm max

	direccio = 1

	num_steps = abs(x_fi-x_ini)*(8000/14)
	if x_fi < x_ini: # si s'ha de girar la direccio
		direccio = 0

	temps_per_step = ( math.sqrt(pow(x_ini-x_fi, 2) + pow(y_ini-y_fi, 2)) / vel)/num_steps

	
	pwm1_ini = valor_proporcional(y_ini, servo_y_min, servo_y_max, servo1_pwm_min, servo1_pwm_max) # calcular la pwm que en teoria te el servo en la posicio y_ini
	pwm1_fi = valor_proporcional(y_fi, servo_y_min, servo_y_max, servo1_pwm_min, servo1_pwm_max)

	pwm1 = pwm1_ini

	pwm2_ini = valor_proporcional(y_ini, servo_y_min, servo_y_max, servo2_pwm_min, servo2_pwm_max)
	pwm2_fi = valor_proporcional(y_fi, servo_y_min, servo_y_max, servo2_pwm_min, servo2_pwm_max)

	pwm2 = pwm2_ini

	# determinar direccions dels steppers
	if direccio == 0: # va cap a X negatives
		if not stepper1_invertit:
			a.board.digitalWrite(a.PIN_STEPPER_1_DIR, "LOW")
		else:
			a.board.digitalWrite(a.PIN_STEPPER_1_DIR, "HIGH")

		if not stepper2_invertit:
			a.board.digitalWrite(a.PIN_STEPPER_2_DIR, "LOW")
		else:
			a.board.digitalWrite(a.PIN_STEPPER_2_DIR, "HIGH")
	else:	# va a X positives
		if stepper1_invertit:
			a.board.digitalWrite(a.PIN_STEPPER_1_DIR, "LOW")
		else:
			a.board.digitalWrite(a.PIN_STEPPER_1_DIR, "HIGH")

		if stepper2_invertit:
			a.board.digitalWrite(a.PIN_STEPPER_2_DIR, "LOW")
		else:
			a.board.digitalWrite(a.PIN_STEPPER_2_DIR, "HIGH")


	# PROBLEMA IMPORTANT: per cada step dels steppers, primer es posen els servos a la posicio Y objectiu i despres es fa el step dels steppers. No pasa res si la linia que segueixen no es basicament vertical, pero si es molt vertical llavors per cada step dels steppers els servos han de fer un desplaçament molt gran de cop, anant a una velocitat molt mes gran de la que es vol.
	# PROBLEMA IMPORTANT 2: no es possible fer desplaçaments completament verticals perque llavors no es fa cap step de stepper.

	# SOLUCIO PROVISIONAL: si el limita com de verticals son els moviments a per exemple 80 graus s'eviten el 2 problemes.

	for i in range(int(num_steps)): # per cada step dels steppers

		# iniciar step stepper
		a.board.digitalWrite(a.PIN_STEPPER_1_STEP, "HIGH")
		a.board.digitalWrite(a.PIN_STEPPER_2_STEP, "HIGH")

		# cambiar pwm servo (va de 0 a 255)
		a.board.analogWrite(a.PIN_SERVO_1, int(pwm1))
		pwm1 += (pwm1_fi-pwm1_ini)/num_steps

		a.board.analogWrite(a.PIN_SERVO_2, int(pwm2))
		pwm2 += (pwm2_fi-pwm2_ini)/num_steps

		# esperar temps/2
		t.sleep(temps_per_step/2)

		# acabar step stepper
		a.board.digitalWrite(a.PIN_STEPPER_1_STEP, "LOW")
		a.board.digitalWrite(a.PIN_STEPPER_2_STEP, "LOW")

		# esperar temps/2
		t.sleep(temps_per_step/2)

	a.board.close()

	return x_fi, y_fi

# mira que ningun segment del trajecte sigui massa vertical
def revisar(llista_punts):

	x_ini, y_ini = (0, 0)

	for p in llista_punts:
		if p[0] == 0 and p[1] == 0:
			continue

		x_fi, y_fi = p
		# mirar que els moviments no siguin molt verticals
		ratio = abs(y_fi-y_ini)/abs(x_fi-x_ini)
		angle = math.atan(ratio)*57.3

		if 90-angle < 10: # si es massa vertical
			return -1

		x_ini = x_fi
		y_ini = y_fi

	return 1


# quan es crida aquesta funcio el punt on esta actualment la cnc passa a ser X = 0
# llista_punts es una llista de tuples, el primer element d'una tupa es una coordenada x i el segon es una coordenada y
def fer_trajecte(llista_punts, velocitat, servo_info, stepper1_invertit, stepper2_invertit, a):

	if revisar(llista_punts) == -1: # mira que ningun trajecte entre punts sigui massa vertical
		return -1, -1

	# posar els servos en el seu lloc mes baix, els steppers no es toquen, el punt on estan passa a ser el punt on X = 0
	a.board.analogWrite(a.PIN_SERVO_1, servo_info[0])
	a.board.analogWrite(a.PIN_SERVO_2, servo_info[2])


	x, y = (0, 0)

	for p in llista_punts:
		x, y = anar_a_punt(x, y, llista_punts[0], llista_punts[1], velocitat, servo_info, stepper1_invertit, stepper2_invertit, a)
		if x == -1 or y == -1:
			return x, y

	return x, y # retorna la posicio final on esta la cnc


