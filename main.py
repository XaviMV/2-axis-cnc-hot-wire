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

def show_success(info):
	CTkMessagebox(title="Success", message=info, icon="check", corner_radius=0)

def show_error(info):
	CTkMessagebox(title="Error", message=info, icon="cancel", corner_radius=0)

class App(ctk.CTk):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.a = arduino_info()

		self.geometry("600x400")

		self.button_calibrate = ctk.CTkButton(self, text="Calibrate", command=self.calibrate)
		self.button_calibrate.grid(row=0, column=0, padx=20, pady=20)

		self.button_draw_path = ctk.CTkButton(self, text="Draw path", command=self.draw_path)
		self.button_draw_path.grid(row=0, column=1, padx=20, pady=20)

		self.button_execute_path = ctk.CTkButton(self, text="Execute path", command=self.execute_path)
		self.button_execute_path.grid(row=0, column=2, padx=20, pady=20)

		self.path_options = os.listdir(os.path.join(os.getcwd(), "data", "created_paths"))
		self.path_file_choice = ctk.CTkComboBox(self, values=self.path_options, command=self.update_combobox)
		self.path_file_choice.grid(row=1, column=2, padx=20, pady=20)
		self.path_file_choice.set("")

		self.toplevel_window = None

	def open_toplevel(self):
		if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
			self.toplevel_window = ErrorWindow(self)  # create window if its None or destroyed
		else:
			self.toplevel_window.focus()  # if window exists focus it

	def calibrate(self):
		calibrar(self.a)
		show_success("Calibration settings have been updated")

	def draw_path(self):
		dialog = ctk.CTkInputDialog(text="Name of the path to be created:", title="Path naming")
		entrada = dialog.get_input()

		# teure tots els espais a l'esquerra del primer caracter i a la dreta de l'ultim
		entrada = entrada.strip()

		if entrada != None and entrada != "" and not (entrada in os.listdir(os.path.join(os.getcwd(), "data", "created_paths"))):

			_, _, _, _, _, _, max_y_height = llegir_calibracio()

			punts = dibuixar_trajecte(max_y_height)

			guardar_path(entrada, punts)

			show_success("The path has been saved!")

		elif entrada != None and entrada != "":
			show_error("The file name is already in use")
		elif entrada != None:
			show_error("The file name cannot be empty")

	def execute_path(self):
		
		min_pwm1, max_pwm1, min_pwm2, max_pwm2, stepper1_invertit, stepper2_invertit, max_y_height = llegir_calibracio()
		
		servo_info = min_pwm1, max_pwm1, min_pwm2, max_pwm2, 0, max_y_height

		nom_arxiu = self.path_file_choice.get()

		trobat = False

		for arx in os.listdir(os.path.join(os.getcwd(), "data", "created_paths")):
			if arx == nom_arxiu:
				trobat = True

		if not trobat:
			show_error("The file couldn't be found")
			return

		punts = llegir_path(nom_arxiu)

		x, y = fer_trajecte(punts, 1, servo_info, stepper1_invertit, stepper2_invertit, self.a)

	def update_combobox(self, box_value):
		self.path_options = os.listdir(os.path.join(os.getcwd(), "data", "created_paths"))
		self.path_file_choice.configure(values=self.path_options)


app = App()
app.mainloop()