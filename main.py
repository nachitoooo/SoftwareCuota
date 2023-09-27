import tkinter as tk
from tkinter import ttk, Scrollbar, messagebox
import csv
import time
import threading
import os
import datetime
from PIL import Image, ImageTk


def restar_dia_global():
    try:
        with open("ultima_resta.txt", "r") as file:
            ultima_resta_str = file.read()
            if ultima_resta_str:
                ultima_resta = datetime.datetime.strptime(ultima_resta_str, "%Y-%m-%d %H:%M:%S")
            else:
                ultima_resta = datetime.datetime(2000, 1, 1)
    except FileNotFoundError:
        ultima_resta = datetime.datetime(2000, 1, 1)    

    ahora = datetime.datetime.now()

    tiempo_transcurrido = ahora - ultima_resta

    if tiempo_transcurrido.total_seconds() >= 24 * 60 * 60:
        clientes = cargar_datos()
        for cliente in clientes:
            dias_restantes = int(cliente[3])
            if dias_restantes > 0:
                dias_restantes -= 1
            cliente[3] = str(dias_restantes)
        guardar_datos(clientes)

        with open("ultima_resta.txt", "w") as file:
            file.write(ahora.strftime("%Y-%m-%d %H:%M:%S"))

    tiempo_espera = 24 * 60 * 60
    threading.Timer(tiempo_espera, restar_dia_global).start()

def cargar_datos():
    clientes = []
    with open("clientes.csv", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            clientes.append(row)
    return clientes

def guardar_datos(clientes):
    with open("clientes.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(clientes)

def agregar_cliente(entry_dni, entry_nombre, entry_apellido):
    dni = entry_dni.get()
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()

    if dni and nombre and apellido:
        with open("clientes.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([nombre, dni, apellido, 30])

        entry_dni.delete(0, tk.END)
        entry_nombre.delete(0, tk.END)
        entry_apellido.delete(0, tk.END)

def eliminar_cliente(cliente, lista_clientes):
    result = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este cliente?")
    if result:
        dni_cliente = cliente[1]
        lista_clientes.delete(tk.ACTIVE)
        clientes = cargar_datos()
        for c in clientes:
            if c[1] == dni_cliente:
                clientes.remove(c)
                break
        guardar_datos(clientes)

def ver_clientes():
    clientes = cargar_datos()
    if hasattr(ver_clientes, 'ventana_clientes') and ver_clientes.ventana_clientes.winfo_exists():
        ventana_clientes = ver_clientes.ventana_clientes
        ventana_clientes.title("Clientes")
    else:
        ventana_clientes = tk.Toplevel()
        ventana_clientes.title("Lista de Clientes")
        ver_clientes.ventana_clientes = ventana_clientes

    ventana_clientes.configure(bg="black")  # Fondo negro

    lista_clientes_label = tk.Label(ventana_clientes, text="Lista de Clientes", fg="white", bg="black", font=("Helvetica", 18, "bold"))
    lista_clientes_label.pack()

    lista_clientes = tk.Listbox(ventana_clientes, bg="black", fg="white", height=15, width=60, font=("Helvetica", 12))
    lista_clientes.pack()

    scrollbar = Scrollbar(ventana_clientes, command=lista_clientes.yview, bg="black", troughcolor="gray")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lista_clientes.config(yscrollcommand=scrollbar.set)

    for cliente in clientes:
        nombre_cliente = cliente[0]
        dni_cliente = cliente[1]
        apellido_cliente = cliente[2]
        dias_restantes = int(cliente[3])
        adeuda_dias = f"{dias_restantes} días restantes" if dias_restantes > 0 else "Al día"
        lista_clientes.insert(tk.END, f"{nombre_cliente} {apellido_cliente} - DNI: {dni_cliente} - {adeuda_dias}")

def verificar_dni():
    dni_a_verificar = entry_dni_a_verificar.get()
    
    clientes = cargar_datos()
    

    dni_encontrado = False
    for cliente in clientes:
        if cliente[1] == dni_a_verificar:
            dni_encontrado = True
            dias_restantes = int(cliente[3])
            if dias_restantes > 0:
                messagebox.showinfo("DNI Encontrado", f"El DNI {dni_a_verificar} se encuentra en la base de datos. Quedan {dias_restantes} días.")
            else:
                messagebox.showinfo("DNI Encontrado", f"El DNI {dni_a_verificar} se encuentra en la base de datos. Está al día.")
            break

    if not dni_encontrado:
        messagebox.showerror("DNI no encontrado", f"El DNI {dni_a_verificar} no se encuentra en la base de datos.")

def crear_interfaz():
    root = tk.Tk()
    root.title("Control de membresía de gimnasio")
    root.geometry("600x600")
    root.configure(bg="black")  # Fondo negro

    cargar_datos()

    # Marco principal para centrar
    frame_main = tk.Frame(root, bg="black")  # Fondo negro
    frame_main.pack(expand=True, fill="both")
    
    logo_path = os.path.join("img", "logo_gimnasio.png")  # Asegúrate de tener la imagen del logo en la carpeta "img"
    if os.path.exists(logo_path):
     logo_image = Image.open(logo_path)

    nuevo_ancho = 300
    nuevo_alto = 300 
    logo_image = logo_image.resize((nuevo_ancho, nuevo_alto), Image.ANTIALIAS)

    # Convertir la imagen redimensionada a PhotoImage para tkinter
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Luego, puedes usar logo_photo en tu etiqueta de imagen
    logo_label = tk.Label(frame_main, image=logo_photo, bg="black")
    logo_label.image = logo_photo
    logo_label.pack(pady=10)

    # Marco para agregar nuevos clientes
    frame_nuevo_cliente = tk.Frame(frame_main, bg="black", bd=3, relief=tk.RIDGE, padx=20, pady=20)
    frame_nuevo_cliente.pack(padx=10, pady=10, expand=True)

    # Etiquetas y campos de entrada para agregar nuevos clientes
    ttk.Label(frame_nuevo_cliente, text="DNI:", background="black", font=("Helvetica", 12), foreground="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_dni = tk.Entry(frame_nuevo_cliente, font=("Helvetica", 12))
    entry_dni.grid(row=0, column=1, padx=10, pady=10)

    ttk.Label(frame_nuevo_cliente, text="Nombre:", background="black", font=("Helvetica", 12), foreground="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_nombre = tk.Entry(frame_nuevo_cliente, font=("Helvetica", 12))
    entry_nombre.grid(row=1, column=1, padx=10, pady=10)

    ttk.Label(frame_nuevo_cliente, text="Apellido:", background="black", font=("Helvetica", 12), foreground="white").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_apellido = tk.Entry(frame_nuevo_cliente, font=("Helvetica", 12))
    entry_apellido.grid(row=2, column=1, padx=10, pady=10)

    boton_agregar_cliente = tk.Button(frame_nuevo_cliente, text="Agregar cliente", command=lambda: agregar_cliente(entry_dni, entry_nombre, entry_apellido), bg="green", fg="white", font=("Helvetica", 12, "bold"), relief=tk.RAISED)
    boton_agregar_cliente.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    boton_verificar_dni = tk.Button(frame_main, text="Verificar DNI", command=verificar_dni, bg="orange", fg="white", font=("Helvetica", 12, "bold"), relief=tk.RAISED)
    boton_verificar_dni.pack(pady=10)

    # Cuadro de entrada para DNI a verificar
    ttk.Label(frame_main, text="DNI a verificar:", background="black", font=("Helvetica", 12), foreground="white").pack(pady=5)
    global entry_dni_a_verificar
    entry_dni_a_verificar = tk.Entry(frame_main, font=("Helvetica", 12))
    entry_dni_a_verificar.pack(pady=5)

    boton_ver_clientes = tk.Button(frame_main, text="Ver Clientes", command=ver_clientes, bg="blue", fg="white", font=("Helvetica", 12, "bold"), relief=tk.RAISED)
    boton_ver_clientes.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    restar_dia_global()
    crear_interfaz()
