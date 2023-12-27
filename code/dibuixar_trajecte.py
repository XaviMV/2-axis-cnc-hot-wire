import pygame
import cv2
import numpy as np
import os

def dibuixar(screen, punts, curr_y_height, max_y_height, mida_quadrat, mostrar_quarats, img, coords_img, mostrar_imatge, img_shape):
	
	# dibuixar canvas
	pygame.draw.rect(screen, (255,255,255), (100,100,1400,600))

	# dibuixar imatge
	if type(img) != list and mostrar_imatge:
		screen.blit(img, (coords_img[0], coords_img[1] - img_shape[0]))

	# dibuixar el fons
	pygame.draw.rect(screen, (50,50,50), (0,0,100,800))
	pygame.draw.rect(screen, (50,50,50), (0,0,1500,100))
	pygame.draw.rect(screen, (50,50,50), (1500,0,100,800))
	pygame.draw.rect(screen, (50,50,50), (0,700,1500,100))

	# dibuixar els punts i lines
	if len(punts) > 1:
		pygame.draw.lines(screen, (0,0,0), False, punts)

	for p in punts:
		pygame.draw.circle(screen, (0,0,255), (p[0], p[1]), 2)

	# dibuixar botó borrar ultim punt
	pygame.draw.rect(screen, (255,255,255), (626,721,348,48))
	pygame.draw.rect(screen, (0,0,0), (630,725,340,40))

	myfont = pygame.font.SysFont("monospace", 30)
	label = myfont.render("Remove last point", 10, (255,150,0))
	screen.blit(label, (650, 727))

	# dibuixar Y max i dibuixar linia max_y_height
	y_offset = 600 - 600/(curr_y_height/max_y_height)

	myfont = pygame.font.SysFont("monospace", 40)
	label = myfont.render(str(max_y_height)+"cm", 10, (255,255,100))
	screen.blit(label, (10, 100 + y_offset - 25))

	pygame.draw.line(screen, (255,0,0), (100, 100 + y_offset), (1500, 100 + y_offset), width = 7)

	# dibuixar distancia X
	myfont = pygame.font.SysFont("monospace", 40)
	label = myfont.render(str(float(int(curr_y_height*100*(1400/600))/100))+"cm", 10, (255,255,100))
	screen.blit(label, (700, 50))

	# dibuixar text mida quadrats
	myfont = pygame.font.SysFont("monospace", 25)
	label = myfont.render(str(int(mida_quadrat*10)/10)+"cm square", 10, (255,255,100))
	screen.blit(label, (50, 740))

	# dibuixar botons canviar mida quadrats
	pygame.draw.polygon(screen, (100,100,100), ((270, 730),(250,750),(290,750)))
	pygame.draw.polygon(screen, (100,100,100), ((270, 780),(250,760),(290,760)))

	# dibuixar bot mostrar quadrats
	color_boto = (10,10,10)
	if not mostrar_quarats:
		color_boto = (50,150,50)

	pygame.draw.rect(screen, (255,255,255), (315,735,40,40))
	pygame.draw.rect(screen, color_boto, (319,739,32,32))

	myfont = pygame.font.SysFont("monospace", 25)
	label = myfont.render("Hide squares", 10, (255,255,100))
	screen.blit(label, (365, 740))

	# dibuixar quadrats, si son molt petits no es dibuixen
	if mostrar_quarats:
		offset_x = 1400/ (curr_y_height*1400/600) * mida_quadrat
		x = 100
		while (x <= 1500 and offset_x > 4):
			pygame.draw.line(screen, (0,0,0), (int(x), 100), (int(x), 700))
			x += offset_x

		offset_y = 600/ curr_y_height * mida_quadrat
		y = 700
		while (y >= 100 and offset_y > 4):
			pygame.draw.line(screen, (0,0,0), (100, int(y)), (1500, int(y)))
			y -= offset_y

	# dibuixar text i botons resize imatge
	myfont = pygame.font.SysFont("monospace", 25)
	label = myfont.render("Img size", 10, (255,255,100))
	screen.blit(label, (1000, 740))
	pygame.draw.polygon(screen, (100,100,100), ((1160, 730),(1140,750),(1180,750)))
	pygame.draw.polygon(screen, (100,100,100), ((1160, 780),(1140,760),(1180,760)))

	# dibuixar boto toggle imatge
	color_boto = (10,10,10)
	if not mostrar_imatge:
		color_boto = (50,150,50)

	pygame.draw.rect(screen, (255,255,255), (1200,735,40,40))
	pygame.draw.rect(screen, color_boto, (1204,739,32,32))

	myfont = pygame.font.SysFont("monospace", 25)
	label = myfont.render("Toggle image", 10, (255,255,100))
	screen.blit(label, (1255, 740))

	# dibuixar botons modificar curr_y_height
	pygame.draw.rect(screen, (100,100,100), (1530, 100, 20, 600))
	pygame.draw.rect(screen, (200,200,200), (1523, y_offset+100-7, 34, 14))
	pygame.draw.rect(screen, (0,0,0), (1525, y_offset+100-5, 30, 10))




def detectar_clicks(events, curr_y_height, max_y_height): # retorna els clicks si estan dintre del canvas

	x, y = pygame.mouse.get_pos()

	borrar_ultim_punt = 0

	quadrats_mes_grans, quadrats_mes_petits = 0, 0

	boto_mostrar_quarats = 0

	boto_resize_up, boto_resize_down = 0, 0

	toggle_image = 0

	slider_moure_altura = 0

	for e in events:
		if e.type == pygame.MOUSEBUTTONDOWN:
			if x > 100 and x < 1500 and y > 100 + 600 - 600/(curr_y_height/max_y_height) and y < 700: # clicar dintre del canvas
				return x, y, borrar_ultim_punt, quadrats_mes_grans, quadrats_mes_petits, boto_mostrar_quarats, boto_resize_up, boto_resize_down, toggle_image, slider_moure_altura
			if x > 630 and x < 630+340 and y  > 725 and y < 725+40: # clicar el boto de borrar l'últim punt
				borrar_ultim_punt = 1

			# botons canviar de mida els quadrats de referencia
			if x > 250 and x < 290 and y > 730 and y < 750:
				quadrats_mes_grans = 1
			if x > 250 and x < 290 and y > 760 and y < 780:
				quadrats_mes_petits = 1

			# boto toggle de visivilitat dels quadrats
			if x > 315 and x < 355 and y > 735 and y < 775:
				boto_mostrar_quarats = 1

			# botons resize de la imatge
			if x > 1140 and x < 1180 and y > 730 and y < 750:
				boto_resize_up = 1
			if x > 1140 and x < 1180 and y > 760 and y < 780:
				boto_resize_down = 1

			# boto toggle imatge
			if x > 1200 and x < 1240 and y > 735 and y < 775:
				toggle_image = 1

	if pygame.mouse.get_pressed()[0]:
		# slider moure altura
		if x > 1500 and x < 1600 and y > 100 and y < 675:
			slider_moure_altura = y


	return -1, -1, borrar_ultim_punt, quadrats_mes_grans, quadrats_mes_petits, boto_mostrar_quarats, boto_resize_up, boto_resize_down, toggle_image, slider_moure_altura


def dibuixar_trajecte(max_y_height): # obra finestra PyGame per marcar els punts del trajecte, retornar una llista d'aquests punts

	curr_y_height = max_y_height

	creant_trajecte = True

	punts = [(100, 700)]
	mida_quadrat = 1.0 # en cm
	mostrar_quarats = True
	mostrar_imatge = True

	coords_img = (100, 700)
	img_resize_factor = 1

	pygame.init()
	screen = pygame.display.set_mode((1600, 800))
	pygame.display.set_caption('Path creation')
	clock = pygame.time.Clock()
	while creant_trajecte: # objectiu de la clalibracio es veure quins son els valors pwm maxims i minims de cada servo

		img_shape = 0

		# tractar la imatge
		img = llegir_imatge()
		if len(img) > 1:
			img = cv2.resize(img, (int(img.shape[1]*img_resize_factor), int(img.shape[0]*img_resize_factor)))
			img_shape = img.shape
			img = cv2.flip(img, 1)
			img = np.rot90(img)
			img = pygame.surfarray.make_surface(img)

		# mirar events
		events = pygame.event.get()
		for e in events:
			if e.type == pygame.QUIT:
				creant_trajecte = False

		# detectar clicks
		x, y, borrar_ultim_punt, quadrats_mes_grans, quadrats_mes_petits, boto_mostrar_quarats, boto_resize_up, boto_resize_down, toggle_image, slider_moure_altura = detectar_clicks(events, curr_y_height, max_y_height)

		if slider_moure_altura != 0:
			curr_y_height = -600/(slider_moure_altura-100-600) * max_y_height


		if borrar_ultim_punt and len(punts) > 1:
			punts.pop()

		if x != -1 and y != -1:
			punts.append((x, y))

		if quadrats_mes_grans:
			mida_quadrat += 0.1
		if quadrats_mes_petits:
			mida_quadrat -= 0.1

		if mida_quadrat > curr_y_height:
			mida_quadrat = curr_y_height
		if mida_quadrat < 0.1:
			mida_quadrat = 0.1

		if boto_mostrar_quarats == 1:
			mostrar_quarats = not mostrar_quarats

		if boto_resize_up:
			img_resize_factor *= 1/0.975

		if boto_resize_down:
			img_resize_factor *= 0.975

		if toggle_image:
			mostrar_imatge = not mostrar_imatge

		# dibuixar pantalla
		screen.fill((50,50,50))
		dibuixar(screen, punts, curr_y_height, max_y_height, mida_quadrat, mostrar_quarats, img, coords_img, mostrar_imatge, img_shape)

		# actualitzar pantalla
		pygame.display.update()
		clock.tick(20)

	pygame.quit()

	punts = punts_canvas_a_reals(punts, curr_y_height)

	return punts

def llegir_imatge():

	arxiu = ""
	img = [[(0,0,0)]]

	for a in os.listdir(os.getcwd()):
		if ".png" in a or ".jpg" in a:
			arxiu = a

	if arxiu != "":
		img = cv2.imread(arxiu)

	return img

def punts_canvas_a_reals(punts, curr_y_height):

	# el canvas es de 600x1400
	punts_reals = []

	for p in punts:

		x = p[0]-100
		y = 600-(p[1]-100)

		y = (y/600)*curr_y_height

		x = x/1400*(curr_y_height*(1400/600))

		punts_reals.append((x, y))

	return punts_reals

def guardar_path(nom, punts):

	data = []

	for p in punts:
		data.append(str(p[0]) + " " + str(p[1]))

	with open("data/created_paths/"+nom, 'w') as file:
		for linia in data:
			if not "\n" in linia:
				linia += "\n"
			file.write(linia)

def llegir_path(nom):

	llista_punts = []

	if os.path.exists("data/created_paths/"+nom):
		with open("data/created_paths/"+nom, 'r') as file:
			linies = file.readlines()
			for l in linies:
				x, y = l.split(" ")
				llista_punts.append((float(x), float(y)))

	return llista_punts