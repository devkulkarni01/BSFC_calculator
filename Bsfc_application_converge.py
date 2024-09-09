'''
Data visualizer 
By Devdatta
'''

import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson
from numpy import trapz as tp
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# center the window on the screen
def center_window(window, width=800, height=600):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# open the file dialog box
def open_file():
    file_path = filedialog.askopenfilename(title="Select Engine Output File from CONVERGE CFD")
    if file_path:
        input_window(file_path)
    else:
        messagebox.showwarning("Please select a valid input file")

# create a window for user input (RPM, Mass of Fuel etc)
def input_window(filename):
    input_win = tk.Toplevel(root)
    input_win.title("Input Engine RPM, Fuel Mass")
    center_window(input_win, 400, 400)

    tk.Label(input_win, text="Enter Engine RPM:", font=("Arial", 14)).pack(pady=10)
    rpm_entry = tk.Entry(input_win, font=("Arial", 14))
    rpm_entry.pack(pady=5)

    tk.Label(input_win, text="Enter Fuel Mass (kg):", font=("Arial", 14)).pack(pady=10)
    fuel_entry = tk.Entry(input_win, font=("Arial", 14))
    fuel_entry.pack(pady=5)

    def submit_input():
        try:
            rpm = int(rpm_entry.get())
            mass_fuel = float(fuel_entry.get())
            input_win.destroy()
            process_file(filename, rpm, mass_fuel)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for RPM and Fuel Mass.")

    submit_btn = tk.Button(input_win, text="Submit", font=("Arial", 14), command=submit_input)
    submit_btn.pack(pady=20)

# calculate values
def process_file(filename, rpm=1500, mass_fuel=20/pow(10,9)):
    column_no = []
    data_print = []

    print_for = 5  # Enter the column number for which plot is required
    plot_x_1 = 8  # For comparison plot
    p_1, p_2 = [], []
    plot_x_name, unit_x = [], []
    plot_y_2, unit_y = 2, []
    plot_y_name = []
    column_name, unit = [], []
    line_count = 0
    p, v, check = [], [], []

    x = ['CONVERGE']  # Value to check compatibility

    for line in open(filename):
        if '#' in line:
            line_count += 1

        if line_count == 1:
            check.append(str(line.split()[1]))

        if check != x:
            messagebox.showerror("Error", "Please provide a valid CONVERGE file.")
            return

        if line_count == 3:
            column_name.append(str(line.split()[print_for]))
            plot_y_name.append(str(line.split()[plot_y_2]))
            plot_x_name.append(str(line.split()[plot_x_1]))

        if line_count == 4:
            unit.append(str(line.split()[print_for]))
            unit_y.append(str(line.split()[plot_y_2]))
            unit_x.append(str(line.split()[plot_x_1]))

        if '#' not in line:
            data_print.append(float(line.split()[print_for - 1]))
            p_1.append(float(line.split()[plot_x_1 - 1]))
            p_2.append(float(line.split()[plot_y_2 - 1]))
            p.append(float(line.split()[1]))
            v.append(float(line.split()[7]))

    # Calculating area under PV diagram
    area = tp(p, v)
    power = ((2 * math.pi * rpm * area) / 60) * 1000
    SFC = (mass_fuel * 1500 * 60) / power

    result_window(area, power, SFC, data_print, column_name[0], unit[0], p_1, p_2, plot_x_name[0], unit_x[0], plot_y_name[0], unit_y[0])

# display results
def result_window(area, power, SFC, data_print, column_name, unit, p_1, p_2, plot_x_name, unit_x, plot_y_name, unit_y):
    result_win = tk.Toplevel(root)
    result_win.title("Calculation Results")
    center_window(result_win, 800, 600)

    result_text = f"Area Under PV Diagram: {area:.8f} N-m\n"
    result_text += f"Power Output: {power:.6f} kW\n"
    result_text += f"Brake Specific Fuel Consumption: {SFC:.6f} kg/kWh"
    
    tk.Label(result_win, text=result_text, font=("Arial", 14), justify=tk.LEFT).pack(pady=10)

    plots = []
    
    
    fig1, ax1 = plt.subplots()
    ax1.plot(data_print)
    ax1.set_xlabel(f"{column_name} {unit}", fontsize=14)
    ax1.set_title(f"Plot for {column_name}", fontsize=20, color='r')
    plots.append(fig1)

    
    fig2, ax2 = plt.subplots()
    ax2.plot(p_1, p_2)
    ax2.set_title(f"Plot for {plot_y_name} vs {plot_x_name}", color='r', fontsize=20)
    ax2.set_xlabel(f"{plot_x_name} {unit_x}", fontsize=14)
    ax2.set_ylabel(f"{plot_y_name} {unit_y}", fontsize=14)
    plots.append(fig2)

    
    plot_index = [0]
    
    canvas = FigureCanvasTkAgg(plots[plot_index[0]], master=result_win)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    canvas.draw()

    def show_next_plot():
        plot_index[0] = (plot_index[0] + 1) % len(plots)  # Circular toggle
        canvas.figure = plots[plot_index[0]]
        canvas.draw()

    def show_previous_plot():
        plot_index[0] = (plot_index[0] - 1) % len(plots)  # Circular toggle
        canvas.figure = plots[plot_index[0]]
        canvas.draw()

    # Arrow buttons
    previous_btn = tk.Button(result_win, text="Previous Plot", font=("Arial", 14), command=show_previous_plot)
    previous_btn.pack(side=tk.LEFT, padx=20, pady=20)

    next_btn = tk.Button(result_win, text="Next Plot", font=("Arial", 14), command=show_next_plot)
    next_btn.pack(side=tk.RIGHT, padx=20, pady=20)

# main window
root = tk.Tk()
root.title("BSFC Calculator")
center_window(root, 800, 600)

# Title
title_label = tk.Label(root, text="Select Engine Output File", font=("Arial", 20))
title_label.pack(pady=20)

# Import Buttons
import_button = tk.Button(root, text="Import File", font=("Arial", 14), command=open_file)
import_button.pack(pady=10)

# Start the application
root.mainloop()
