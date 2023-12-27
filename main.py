import math
import os

from code.funcions_arduino import iniciar_board, arduino_info
from code.calibrar import calibrar
from code.dibuixar_trajecte import dibuixar_trajecte, guardar_path, llegir_path
from code.fer_trajecte import fer_trajecte


# POSICIO DEL ORIGEN: el punt (0, 0) esta amb la x al cap de la maquina i la y en la posicio mes baixa


# hi ha un try dintre de la creacio de la classe per si no esta conectada ningua arduino
a = arduino_info()

while True:

	print("Que vols fer?")
	print("    1.- Calibrar")
	print("    2.- Crear trajecte")
	print("    3.- Fer trajecte")
	print("    4.- Sortir")

	entrada = int(input())



	if entrada == 1:
		min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height = calibrar(a)

	elif entrada == 2:
		punts = dibuixar_trajecte(4)

		print("Quin nom li vols posar al path creat? Deixa buit per no posar nom.")

		nom = input()
		if nom != " " and len(nom) != 0:
			guardar_path(nom, punts)

	elif entrada == 3:

		min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height = calibrar(a)
		
		servo_info = min_pwm1, max_pwm1, min_pwm2, max_pwm2, 0, max_y_height

		print("De quin arxiu guardat vols llegir el path a fer?")

		for arx in os.listdir("data/created_paths"):
			print(arx)

		nom_arxiu = input()

		punts = llegir_path(nom_arxiu)

		print(punts)

		x, y = fer_trajecte(punts, 1, servo_info, stepper1_invertit, stepper2_invertit, a)
	
	elif entrada == 4:
		break