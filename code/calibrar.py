import pygame
from code.funcions_arduino import moure_servos, moure_steppers, arduino_info

# Fitxer per guardar les funcions relacionades amb calibrar la cnc


# per determinar la direccio i posicio dels steppers i fixar els punts maxim i minim dels servos
def calibrar(a):
	calibrant = True

	min_pwm1 = 0
	min_pwm2 = 0
	max_pwm1 = 255
	max_pwm2 = 255

	max_y_height = 1 # altura dels servos en la seva posicio mes alta, tenint en compte que la seva posicio mes baixa pepresenta Y = 0

	# invertir
	servo1_invertit = False
	servo2_invertit = False

	stepper1_invertit = 0
	stepper2_invertit = 0

	pwm1 = 128
	pwm2 = 128

	pygame.init()
	screen = pygame.display.set_mode((1280, 720))
	pygame.display.set_caption('Calibration')
	clock = pygame.time.Clock()

	min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height = llegir_calibracio()

	while calibrant: # objectiu de la clalibracio es veure quins son els valors pwm maxims i minims de cada servo

		# mirar events
		events = pygame.event.get()
		for e in events:
			if e.type == pygame.QUIT:
				calibrant = False

		servos_clicats, steppers_clicats, botons_clicats, steppers_invertits, boto_max_y = detect_clicks(events)

		# tractar clics

		if botons_clicats[0]: # sha clicat SET MAX
			max_pwm1 = pwm1
			max_pwm2 = pwm2
		if botons_clicats[1]: # sha clicat SET MIN
			min_pwm1 = pwm1
			min_pwm2 = pwm2
		if botons_clicats[2]: # sha clicat REMOVE MAX
			if not servo1_invertit:
				max_pwm1 = 255
			else:
				max_pwm1 = 0
			if not servo2_invertit:
				max_pwm2 = 255
			else:
				max_pwm2 = 0

		if botons_clicats[3]: # sha clicat REMOVE MIN
			if not servo1_invertit:
				min_pwm1 = 0
			else:
				min_pwm1 = 255
			if not servo2_invertit:
				min_pwm2 = 0
			else:
				min_pwm2 = 255


		if botons_clicats[4]: # invertir servo 1
			servo1_invertit = not servo1_invertit
			min_pwm1, max_pwm1 = max_pwm1, min_pwm1

		if botons_clicats[5]: # invertir servo 2
			servo2_invertit = not servo2_invertit
			min_pwm2, max_pwm2 = max_pwm2, min_pwm2

		if steppers_invertits[0]: # invertir stepper 1
			stepper1_invertit = 1 - stepper1_invertit

		if steppers_invertits[1]: # invertir stepper 2
			stepper2_invertit = 1 - stepper2_invertit


		if boto_max_y: # boto modificar Y max
			max_y_height += 1
			if max_y_height > 9:
				max_y_height = 1


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
		steppers_invertits = [stepper1_invertit, stepper2_invertit]
		dibuixar_gui(screen, pwm1, pwm2, min_pwm1, max_pwm1, min_pwm2, max_pwm2, steppers_clicats, steppers_invertits, max_y_height)

		# actualitzar
		pygame.display.update()
		clock.tick(20)

		# moure els components
		#moure_servos(pwm1, pwm2, a)
		#moure_steppers(steppers_clicats, stepper1_invertit, stepper2_invertit, a)

	pygame.quit()

	guardar_calibracio(min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height)

	return min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height


def dibuixar_gui(screen, pwm1, pwm2, min_pwm1, max_pwm1, min_pwm2, max_pwm2, steppers_clicats, steppers_invertits, max_y_height):

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

		# botons de invertir
		color_boto_invertir_stepper = (0, 0, 0)

		if steppers_invertits[i]:
			color_boto_invertir_stepper = (0, 150, 0)

		pygame.draw.rect(screen, (125,125,125), (380+i*680,545,50,50))
		pygame.draw.rect(screen, color_boto_invertir_stepper, (385+i*680,550,40,40))

		myfont = pygame.font.SysFont("monospace", 40)
		label = myfont.render("I", 10, (255,255,255))
		screen.blit(label, (393+i*680,548))


	# dibuixar els valors de les pwm limit
	myfont = pygame.font.SysFont("monospace", 15)

	label = myfont.render(str(max_pwm1), 10, (255,255,0))
	screen.blit(label, (200+125, 100))
	label = myfont.render(str(min_pwm1), 10, (255,255,0))
	screen.blit(label, (200+125, 225))

	label = myfont.render(str(max_pwm2), 10, (255,255,0))
	screen.blit(label, (200+680+125, 100))
	label = myfont.render(str(min_pwm2), 10, (255,255,0))
	screen.blit(label, (200+680+125, 225))


	# dibuixar el text del valor de les pwm actuals
	myfont = pygame.font.SysFont("monospace", 20)

	label = myfont.render(str(pwm1), 10, (255,255,0))
	screen.blit(label, (200+125, 155))

	label = myfont.render(str(pwm2), 10, (255,255,0))
	screen.blit(label, (200+680+125, 155))

	# dibuixar botons SET MIN, SET MAX i R dels servos
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

	# dibuixar texts "min height" "max height"
	myfont = pygame.font.SysFont("monospace", 20)

	label = myfont.render("max height", 10, (255,255,0))
	screen.blit(label, (545, 95))
	label = myfont.render("min height", 10, (255,255,0))
	screen.blit(label, (545, 227))

	# dibixar l'altura maxima i el seu botó
	myfont = pygame.font.SysFont("monospace", 50)

	label = myfont.render(str(max_y_height)+"cm", 10, (255,150,0))
	screen.blit(label, (545, 20))

	pygame.draw.rect(screen, (200,200,200), (650,35,30,30))
	pygame.draw.rect(screen, (0,0,0), (652,37,26,26))



def detect_clicks(events):

	servos_clicats = [0,0,0,0] # els elements representen: pwm1+, pwm1-, pwm2+, pwm2-

	steppers_clicats = [0,0,0,0, 0,0,0,0] # 4 botons per cada stepper: sumar 1 step, restar 1 step, sumar 30 steps i restar 30 steps

	botons_clicats = [0, 0, 0, 0, 0, 0] # els botons son: set_max, set_min, remove_max, remove_min, invertir1, invertir2 dels servos

	steppers_invertits = [0, 0]

	boto_max_y = 0

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

			for i in range(2): # botons invertir servo
				if x > 225+i*680 and x < 225+i*680+50 and y > 275 and y < 275+50:
					botons_clicats[i+4] = 1

			for i in range(2): # botons invertir stepper
				if x > 380+i*680 and x < 380+i*680+50 and y > 545 and y < 545+50:
					steppers_invertits[i] = 1
			
			if x > 650 and x < 650+30 and y > 35 and y < 35+30: # si es clica el boto de modificar la Y max
				boto_max_y = 1

	return servos_clicats, steppers_clicats, botons_clicats, steppers_invertits, boto_max_y

# guardar les variables tretes d'una calibració en un arxiu per no necessitar calibrar cada cop que es vol fer alguna cosa
def guardar_calibracio(min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height):

	data = []

	with open("data/calibration.txt", "r") as file:
		data = file.readlines()

	if len(data) == 0:
		for i in range(7):
			data.append("")

	# modificar la data
	data[0] = min_pwm1
	data[1] = max_pwm1
	data[2] = min_pwm2
	data[3] = max_pwm2
	data[4] = stepper1_invertit
	data[5] = stepper2_invertit
	data[6] = max_y_height

	for i in range(len(data)):
		data[i] = str(data[i])

	with open("data/calibration.txt", 'w') as file:
		# Write each string in the list to a new line in the file
		for linia in data:
			if not "\n" in linia:
				linia += "\n"
			file.write(linia)

def llegir_calibracio():

	data = []

	with open("data/calibration.txt", "r") as file:
		data = file.readlines()

	min_pwm1 = int(data[0])
	max_pwm1 = int(data[1])
	min_pwm2 = int(data[2])
	max_pwm2 = int(data[3])

	stepper1_invertit = int(data[4])
	stepper2_invertit = int(data[5])

	max_y_height = int(data[6])

	return min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height
