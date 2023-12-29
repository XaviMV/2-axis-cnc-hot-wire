import math
import os
import time as t
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk

from code.funcions_arduino import iniciar_board, arduino_info, moure_servos, moure_steppers
from code.calibrar import calibrar, llegir_calibracio
from code.dibuixar_trajecte import dibuixar_trajecte, guardar_path, llegir_path
from code.fer_trajecte import fer_trajecte

# POSICIO DEL ORIGEN: el punt (0, 0) esta amb la x al cap de la maquina i la y en la posicio mes baixa

def show_success(info, m):
	msg = CTkMessagebox(master=m, title="Success", message=info, icon="check", corner_radius=0)
	msg.get()

def show_error(info, m):
	msg = CTkMessagebox(master=m, title="Error", message=info, icon="cancel", corner_radius=0)
	msg.get()

class App(ctk.CTk):
	def __init__(self):
		super().__init__()

		self.a = arduino_info()

		self.title("CNC")

		w = 650 # width for the app
		h = 225 # height for the app
		ws = self.winfo_screenwidth() # width of the screen
		hs = self.winfo_screenheight() # height of the screen
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		self.geometry('%dx%d+%d+%d' % (w, h, x, y))

		self.frame = ctk.CTkFrame(self)
		self.frame.grid(row=0, column=2, padx=20, pady=20)

		self.button_calibrate = ctk.CTkButton(self, text="Calibrate", command=self.calibrate)
		self.button_calibrate.grid(row=0, column=0, padx=20, pady=20, rowspan=2)

		self.button_draw_path = ctk.CTkButton(self, text="Draw path", command=self.draw_path)
		self.button_draw_path.grid(row=0, column=1, padx=20, pady=20, rowspan=2)

		self.button_execute_path = ctk.CTkButton(self.frame, text="Execute path", command=self.execute_path)
		self.button_execute_path.grid(row=0, column=0, padx=20, pady=20)

		self.path_options = os.listdir(os.path.join(os.getcwd(), "data", "created_paths"))
		self.path_file_choice = ctk.CTkComboBox(self.frame, values=self.path_options, command=self.update_combobox)
		self.path_file_choice.grid(row=1, column=0, padx=20, pady=20)
		self.path_file_choice.set("")


	def calibrate(self):
		calibrar(self.a)
		show_success("Calibration settings have been updated", self)

	def draw_path(self):

		_, _, _, _, _, _, max_y_height = llegir_calibracio()

		punts = dibuixar_trajecte(max_y_height)

		if len(punts) <= 1:
			show_error("The path cannot be created since it is empty", self)
			return

		while True:
			dialog = ctk.CTkInputDialog(text="Name of the path to be created:", title="Path naming")

			# fer que apareixe a sobre de la app
			w = 350
			h = 200
			x, y = self.winfo_x(), self.winfo_y()
			dialog.geometry('%dx%d+%d+%d' % (w, h, x+30, y+30))

			entrada = dialog.get_input()

			if entrada == None: # si se li ha donat a cancel
				show_success("The path has not been saved", self)
				return

			# teure tots els espais a l'esquerra del primer caracter i a la dreta de l'ultim
			entrada = entrada.strip()

			if entrada != None and entrada != "" and not (entrada in os.listdir(os.path.join(os.getcwd(), "data", "created_paths"))):
				guardar_path(entrada, punts)
				show_success("The path has been saved!", self)
				self.command_update_combobox()
				return

			elif entrada != None and entrada != "":
				show_error("That file name is already in use", self)
			elif entrada != None:
				show_error("The file name cannot be empty", self)


	def execute_path(self):
		
		min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height = llegir_calibracio()
		
		servo_info = min_pwm1, max_pwm1, min_pwm2, max_pwm2, 0, max_y_height

		nom_arxiu = self.path_file_choice.get()

		if nom_arxiu == "":
			show_error("You first need to choose a file from the selector below", self)
			return

		trobat = False

		for arx in os.listdir(os.path.join(os.getcwd(), "data", "created_paths")):
			if arx == nom_arxiu:
				trobat = True

		if not trobat:
			show_error("The file couldn't be found", self)
			return

		punts = llegir_path(nom_arxiu)

		x, y = fer_trajecte(punts, 1, servo_info, stepper1_invertit, stepper2_invertit, self.a)

	def command_update_combobox(self):
		self.path_options = os.listdir(os.path.join(os.getcwd(), "data", "created_paths"))
		self.path_file_choice.configure(values=self.path_options)

	def update_combobox(self, box_value):
		self.command_update_combobox()


app = App()

for c in range(3):
	app.grid_columnconfigure(c, weight=1)
for r in range(1):
	app.grid_rowconfigure(r, weight=1)

app.minsize(width=580, height=180)
app.maxsize(width=1920, height=1080)
app.mainloop()