from Arduino import Arduino
import time as t
import math
import pygame

# POSICIO DEL ORIGEN: el punt (0, 0) esta amb la x al cap de la maquina i la y en la posicio mes baixa

# Posicio minima i maxima dels servos
SERVO_Y_MIN = 0
SERVO_Y_MAX = 5


# Pins a utilitzar, mirar que els pins dels servos tinguin implementada la funcionalitat pwm
PIN_SEVO_1 = 9
PIN_SEVO_2 = 10

PIN_STEPPER_1_STEP = 7
PIN_STEPPER_2_STEP = 8

PIN_STEPPER_1_DIR = 5
PIN_STEPPER_2_DIR = 6



def valor_proporcional(valor_ref, valor_ref_min, valor_ref_max, valor_obj_min, valor_obj_max): # retorna el valor_obj proporcional al valor_ref, fa el mateix que la funcio "map" en la arduino

	rang_antic = (valor_ref_max - valor_ref_min)  
	rang_nou = (valor_obj_max - valor_obj_min)  
	valor_obj = (((valor_ref - valor_ref_min) * rang_nou) / rang_antic) + valor_obj_min

	return valor_obj


# INPUT:
# x_ini, y_ini -> punt on es troba la cnc abans d'entrar a la funcio
# x_fi, y_fi -> punt objectiu a on es vol portar la cnc
# vel -> velocitat amb la que es vol anar, en cm/s
# servo_info -> llista amb informacio sobre el servo
def anar_a_punt(x_ini, y_ini, x_fi, y_fi, vel, servo_info):

	# mirar que els moviments no siguin molt verticals
	ratio = abs(y_fi-y_ini)/abs(x_fi-x_ini)
	angle = math.atan(ratio)*57.3

	if 90-angle < 10: # si es massa vertical
		return -1, -1

	servo1_pwm_min, servo1_pwm_max, servo2_pwm_min, servo2_pwm_max, servo_y_min, servo_y_max = servo_info # servo_y_min hauria de ser sempre 0. Pwm min es refereix a la pwm a la altura minima, pwm max a la maxima, per tant pwm_min pot ser mes gran que pwm max

	direccio = 1

	num_steps = abs(x_fi-x_ini)*(1000/14)
	if x_fi < x_ini: # si s'ha de girar la direccio
		direccio = 0

	temps_per_step = ( math.sqrt(pow(x_ini-x_fi, 2) + pow(y_ini-y_fi, 2)) / vel)/num_steps

	
	pwm1_ini = valor_proporcional(y_ini, servo_y_min, servo_y_max, servo1_pwm_min, servo1_pwm_max) # calcular la pwm que en teoria te el servo en la posicio y_ini
	pwm1_fi = valor_proporcional(y_fi, servo_y_min, servo_y_max, servo1_pwm_min, servo1_pwm_max)

	pwm1 = pwm1_ini

	pwm2_ini = valor_proporcional(y_ini, servo_y_min, servo_y_max, servo2_pwm_min, servo2_pwm_max)
	pwm2_fi = valor_proporcional(y_fi, servo_y_min, servo_y_max, servo2_pwm_min, servo2_pwm_max)

	pwm2 = pwm2_ini

	board = Arduino("115200")
	board.pinMode(PIN_STEPPER_1_STEP, "OUTPUT")
	board.pinMode(PIN_STEPPER_2_STEP, "OUTPUT")
	board.pinMode(PIN_STEPPER_1_DIR, "OUTPUT")
	board.pinMode(PIN_STEPPER_2_DIR, "OUTPUT")

	if direccio == 1:
		board.digitalWrite(PIN_STEPPER_1_DIR, 1)
		board.digitalWrite(PIN_STEPPER_2_DIR, 0)
	else:
		board.digitalWrite(PIN_STEPPER_1_DIR, 0)
		board.digitalWrite(PIN_STEPPER_2_DIR, 1)
		
	board.pinMode(PIN_SERVO_1, "OUTPUT")
	board.pinMode(PIN_SERVO_2, "OUTPUT")

	# PROBLEMA IMPORTANT: per cada step dels steppers, primer es posen els servos a la posicio Y objectiu i despres es fa el step dels steppers. No pasa res si la linia que segueixen no es basicament vertical, pero si es molt vertical llavors per cada step dels steppers els servos han de fer un desplaçament molt gran de cop, anant a una velocitat molt mes gran de la que es vol.
	# PROBLEMA IMPORTANT 2: no es possible fer desplaçaments completament verticals perque llavors no es fa cap step de stepper.

	# SOLUCIO PROVISIONAL: si el limita com de verticals son els moviments a per exemple 80 graus s'eviten el 2 problemes.

	for i in range(int(num_steps)): # per cada step dels steppers

		# iniciar step stepper
		board.digitalWrite(PIN_STEPPER_1_STEP, "HIGH")
		board.digitalWrite(PIN_STEPPER_2_STEP, "HIGH")

		# cambiar pwm servo (va de 0 a 255)
		board.analogWrite(PIN_SEVO_1, int(pwm1))
		pwm1 += (pwm1_fi-pwm1_ini)/num_steps

		board.analogWrite(PIN_SEVO_2, int(pwm2))
		pwm2 += (pwm2_fi-pwm2_ini)/num_steps

		# esperar temps/2
		t.sleep(temps_per_step/2)

		# acabar step stepper
		board.digitalWrite(PIN_STEPPER_1_STEP, "LOW")
		board.digitalWrite(PIN_STEPPER_2_STEP, "LOW")

		# esperar temps/2
		t.sleep(temps_per_step/2)


	board.close()

	return x_fi, y_fi

def revisar(llista_punts):

	x_ini, y_ini = (0, 0)

	for p in llista_punts:
		x_fi, y_fi = p
		# mirar que els moviments no siguin molt verticals
		ratio = abs(y_fi-y_ini)/abs(x_fi-x_ini)
		angle = math.atan(ratio)*57.3

		if 90-angle < 10: # si es massa vertical
			return -1

	return 1



# quan es crida aquesta funcio el punt on esta actualment la cnc passa a ser X = 0
# llista_punts es una llista de tuples, el primer element d'una tupa es una coordenada x i el segon es una coordenada y
def fer_trajecte(llista_punts, velocitat, servo_info):

	if revisar(llista_punts) == -1: # mira que ningun trajecte entre punts sigui massa vertical
		return -1, -1

	# posar els servos en el seu lloc mes baix, els steppers no es toquen, el punt on estan passa a ser el punt on X = 0
	board = Arduino("115200")

	board.pinMode(PIN_SERVO_1, "OUTPUT")
	board.pinMode(PIN_SERVO_2, "OUTPUT")

	board.analogWrite(PIN_SEVO_1, servo_info[0])
	board.analogWrite(PIN_SEVO_2, servo_info[2])

	board.close()

	x, y = (0, 0)

	for p in llista_punts:
		x, y = anar_a_punt(x, y, llista_punts[0], llista_punts[1], velocitat, servo_info)
		if x == -1 or y == -1:
			return x, y

	return x, y # retorna la posicio final on esta la cnc


# funcio per moure els sevos amb les pwm donades
def moure_servos(pwm1, pwm2):
	board = Arduino("115200")

	board.pinMode(PIN_SERVO_1, "OUTPUT")
	board.pinMode(PIN_SERVO_2, "OUTPUT")

	board.analogWrite(PIN_SEVO_1, pwm1)
	board.analogWrite(PIN_SEVO_2, pwm2)

	board.close()

def moure_steppers(steppers_clicats):

	# mirar que nomes es cliqui 1 sol boto
	clicat = 0
	for i in range(len(steppers_clicats)):
		if steppers_clicats[i] == 1:
			if clicat != 0: # si es troba un segon boto clicat es para la funcio
				return
			clicat = i

	board = Arduino("115200")

	board.pinMode(PIN_STEPPER_1_STEP, "OUTPUT")
	board.pinMode(PIN_STEPPER_2_STEP, "OUTPUT")

	board.pinMode(PIN_STEPPER_1_DIR, "OUTPUT")
	board.pinMode(PIN_STEPPER_2_DIR, "OUTPUT")

	if clicat % 2 == 0: # S'ha clicat alguna fletxa superior
		board.digitalWrite(PIN_STEPPER_1_DIR, 0)
		board.digitalWrite(PIN_STEPPER_2_DIR, 0)
	else:
		board.digitalWrite(PIN_STEPPER_1_DIR, 1)
		board.digitalWrite(PIN_STEPPER_2_DIR, 1)

	temps_per_step = 0.01
	iteracions = 1
	if clicat == 2 or clicat == 6: # s'han de fer 20 steps (fletxa gran)
		iteracions = 20
		temps_per_step = 0.002
	
	pin_stepper = 0
	if clicat < 4: # stepper 1
		pin_stepper = PIN_STEPPER_1_STEP
	else: # stepper 2
		pin_stepper = PIN_STEPPER_2_STEP

	for i in range(iteracions):
		board.digitalWrite(pin_stepper, 1)
		t.sleep(0.01)
		board.digitalWrite(pin_stepper, 0)
		t.sleep(0.01)

	board.close()



def dibuixar_gui(screen, pwm1, pwm2, min_pwm1, max_pwm1, min_pwm2, max_pwm2, steppers_clicats):

	colors_servos = [(0, 255, 255), (0, 255, 255), (0, 255, 255), (0, 255, 255)] # colors per a la fletxa superior i inferior del servo1, i del servo2

	if pwm1 == max_pwm1:
		colors_servos[0] = (255,0,0)

	if pwm1 == min_pwm1:
		colors_servos[1] = (255,0,0)

	if pwm2 == max_pwm2:
		colors_servos[2] = (255,0,0)

	if pwm2 == min_pwm2:
		colors_servos[3] = (255,0,0)

	for i in range(2): # per cada servo

		# dibuixar els botons (triangle superior i inferior)
		pygame.draw.polygon(screen, colors_servos[i*2], ((250+i*680,85),(200+i*680,135),(300+i*680,135)))
		pygame.draw.polygon(screen, colors_servos[i*2+1], ((250+i*680,250),(200+i*680,200),(300+i*680,200)))

		# dibuixar el text dels servos
		myfont = pygame.font.SysFont("monospace", 30)
		label = myfont.render("SERVO"+str(i+1), 10, (255,255,0))
		screen.blit(label, (200+i*680, 150))

		# dibuixar botons per invertir
		pygame.draw.rect(screen, (125,125,125), (225+i*680,275,50,50))
		pygame.draw.rect(screen, (0,0,0), (230+i*680,280,40,40))

		myfont = pygame.font.SysFont("monospace", 40)
		label = myfont.render("I", 10, (255,255,255))
		screen.blit(label, (238+i*680,277))


	# mirar quin color ha de tenir cada fletxa dels steppers
	colors_steppers = []
	for i in steppers_clicats:
		if i == 1: # si s'ha clicat el boto
			colors_steppers.append((255, 200, 0))
		else:
			colors_steppers.append((0, 255, 255))

	for i in range(2): # per cada stepper

		# dibuixar els botons (2 superior i 2 inferiors, el petit fa 1 step i el gran fa 10)
		pygame.draw.polygon(screen, colors_steppers[i*4], ((200+i*680,505),(170+i*680,535),(230+i*680,535))) # superior 1 step
		pygame.draw.polygon(screen, colors_steppers[i*4+1], ((200+i*680,630),(170+i*680,600),(230+i*680,600))) # inferior 1 step

		pygame.draw.polygon(screen, colors_steppers[i*4+2], ((295+i*680,485),(245+i*680,535),(345+i*680,535))) # superior 10 steps
		pygame.draw.polygon(screen, colors_steppers[i*4+3], ((295+i*680,650),(245+i*680,600),(345+i*680,600))) # inferior 10 steps

		# dibuixar el text de stepper1 i stepper2
		myfont = pygame.font.SysFont("monospace", 40)
		label = myfont.render("STEPPER"+str(i+1), 10, (255,255,0))
		screen.blit(label, (165+i*680,545))



	# dibuixar el valor de les pwm limit
	myfont = pygame.font.SysFont("monospace", 15)

	label = myfont.render(str(max_pwm1), 10, (255,255,0))
	screen.blit(label, (200+125, 100))
	label = myfont.render(str(min_pwm1), 10, (255,255,0))
	screen.blit(label, (200+125, 225))

	label = myfont.render(str(max_pwm2), 10, (255,255,0))
	screen.blit(label, (200+680+125, 100))
	label = myfont.render(str(min_pwm2), 10, (255,255,0))
	screen.blit(label, (200+680+125, 225))


	# dibuixar el text de les pwm actuals
	myfont = pygame.font.SysFont("monospace", 20)

	label = myfont.render(str(pwm1), 10, (255,255,0))
	screen.blit(label, (200+125, 155))

	label = myfont.render(str(pwm2), 10, (255,255,0))
	screen.blit(label, (200+680+125, 155))

	# dibuixar botons SET MIN, SET MAX i R
	for i in range(2):
		pygame.draw.rect(screen, (125,125,125), (485,120+i*50,240,55))
		pygame.draw.rect(screen, (0,0,0), (490,125+i*50,180,45))
		pygame.draw.rect(screen, (0,0,0), (675,125+i*50,45,45))

	myfont = pygame.font.SysFont("monospace", 40)

	label = myfont.render("SET MAX", 10, (255,255,255))
	screen.blit(label, (495, 125))
	label = myfont.render("SET MIN", 10, (255,255,255))
	screen.blit(label, (495, 175))

	label = myfont.render("R", 10, (255,255,255))
	screen.blit(label, (685, 125))
	screen.blit(label, (685, 175))

	# dibuixar "min height" "max height"
	myfont = pygame.font.SysFont("monospace", 20)

	label = myfont.render("max height", 10, (255,255,0))
	screen.blit(label, (545, 95))
	label = myfont.render("min height", 10, (255,255,0))
	screen.blit(label, (545, 227))



def detect_clicks(events):

	servos_clicats = [0,0,0,0] # els elements representen: pwm1+, pwm1-, pwm2+, pwm2-

	steppers_clicats = [0,0,0,0, 0,0,0,0] # 4 botons per cada stepper: sumar 1 step, restar 1 step, sumar 10 steps i restar 10 steps

	botons_clicats = [0, 0, 0, 0, 0, 0] # els botons son: set_max, set_min, remove_max, remove_min dels botons pwm

	x, y = pygame.mouse.get_pos()

	if pygame.mouse.get_pressed()[0]: # si s'esta clicant el ratoli
		for i in range(2): # si s'han clicat botons de canviar pwm
			if x > 200+i*680 and x < 300+i*680 and y > 85 and y < 135:
				servos_clicats[0+i*2] = 1
			if x > 200+i*680 and x < 300+i*680 and y > 200 and y < 250:
				servos_clicats[1+i*2] = 1

		for i in range(2): # botons stepper
			if x > 170+i*680 and x < 230+i*680 and y > 505 and y < 535: # fletxa superior petita
				steppers_clicats[i*4] = 1
			if x > 170+i*680 and x < 230+i*680 and y > 600 and y < 630: # fletxa inferior petita
				steppers_clicats[i*4+1] = 1
			if x > 245+i*680 and x < 345+i*680 and y > 485 and y < 535: # fletxa superior gran
				steppers_clicats[i*4+2] = 1
			if x > 245+i*680 and x < 345+i*680 and y > 600 and y < 650: # fletxa superior gran
				steppers_clicats[i*4+3] = 1



	for e in events: # detectar nomes el moment quan el clica el ratoli, no si es deixa clicat
		if e.type == pygame.MOUSEBUTTONDOWN:
			for i in range(2): # si s'han clicat botons set min o set max
				if x > 490 and x < 490+180 and y > 125+i*50 and y < 125+i*50+45:
					botons_clicats[i] = 1

			for i in range(2): # botons remove min i remove max
				if x > 675 and x < 675+55 and y > 125+i*50 and y < 125+i*50+45:
					botons_clicats[i+2] = 1

			for i in range(2): # botons invertir
				if x > 225+i*680 and x < 225+i*680+50 and y > 275 and y < 275+50:
					botons_clicats[i+4] = 1

	return servos_clicats, steppers_clicats, botons_clicats


# per fixar els punts maxim i minim dels servos
def calibrar():
	calibrant = True

	min_pwm1 = 0
	min_pwm2 = 0
	max_pwm1 = 255
	max_pwm2 = 255


	# invertir
	servo1_invertit = False
	servo2_invertit = False

	stepper1_invertit = False
	stepper2_invertit = False

	pwm1 = 128
	pwm2 = 128

	pygame.init()
	screen = pygame.display.set_mode((1280, 720))
	pygame.display.set_caption('Calibration')
	clock = pygame.time.Clock()

	while calibrant: # objectiu de la clalibracio es veure quins son els valors pwm maxims i minims de cada servo

		# mirar events
		events = pygame.event.get()
		for e in events:
			if e.type == pygame.QUIT:
				calibrant = False

		servos_clicats, steppers_clicats, botons_clicats = detect_clicks(events)

		# tractar clics
		if botons_clicats[0]: # sha clicat SET MAX
			max_pwm1 = pwm1
			max_pwm2 = pwm2
		if botons_clicats[1]: # sha clicat SET MIN
			min_pwm1 = pwm1
			min_pwm2 = pwm2
		if botons_clicats[2]: # sha clicat REMOVE MAX
			max_pwm1 = 255
			max_pwm2 = 255
		if botons_clicats[3]: # sha clicat REMOVE MIN
			min_pwm1 = 0
			min_pwm2 = 0


		if botons_clicats[4]: # invertir servo 1
			servo1_invertit = not servo1_invertit
			min_pwm1, max_pwm1 = max_pwm1, min_pwm1

		if botons_clicats[5]: # invertir servo 2
			servo2_invertit = not servo2_invertit
			min_pwm2, max_pwm2 = max_pwm2, min_pwm2

		# limitar els valors maxims i minims
		if not servo1_invertit:
			if servos_clicats[0] and pwm1 < max_pwm1:
				pwm1 += 1
			if servos_clicats[1] and pwm1 > min_pwm1:
				pwm1 -= 1
		else:
			if servos_clicats[0] and pwm1 > max_pwm1:
				pwm1 -= 1
			if servos_clicats[1] and pwm1 < min_pwm1:
				pwm1 += 1

		if not servo2_invertit:
			if servos_clicats[2] and pwm2 < max_pwm2:
				pwm2 += 1
			if servos_clicats[3] and pwm2 > min_pwm2:
				pwm2 -= 1
		else:
			if servos_clicats[2] and pwm2 > max_pwm2:
				pwm2 -= 1
			if servos_clicats[3] and pwm2 < min_pwm2:
				pwm2 += 1


		# dibuixar
		screen.fill((50,50,50))
		dibuixar_gui(screen, pwm1, pwm2, min_pwm1, max_pwm1, min_pwm2, max_pwm2, steppers_clicats)

		# actualitzar
		pygame.display.update()
		clock.tick(20)

		# moure els components
		#moure_servos(pwm1, pwm2)
		#moure_steppers(steppers_clicats) sha de fer encara

	pygame.quit()

	# preguntar per la altura maxima i minima dels servos en cm (minima ha de ser 0)


	return min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit


calibrar()