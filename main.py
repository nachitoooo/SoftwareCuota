import tkinter as tk
from tkinter import ttk, Scrollbar, messagebox
import csv
import time
import threading
import os
import datetime
from PIL import Image, ImageTk

lista_clientes = None

def apply_button_style(button):
    button.config(
        bg="#E0E0E0", 
        fg="black",    
        font=("Helvetica", 12), 
        relief=tk.RAISED  
    )



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


def agregar_cliente(entry_dni, entry_nombre, entry_apellido, entry_dias):
    dni = entry_dni.get()
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    dias = entry_dias.get()

    if dni and nombre and apellido and dias:
        with open("clientes.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([nombre, dni, apellido, dias]) 

        entry_dni.delete(0, tk.END)
        entry_nombre.delete(0, tk.END)
        entry_apellido.delete(0, tk.END)
        entry_dias.delete(0, tk.END)  

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


def obtener_cliente_seleccionado(lista_clientes):
    seleccion = lista_clientes.curselection()
    if seleccion:
        indice = seleccion[0]
        cliente_seleccionado = lista_clientes.get(indice)
        return cliente_seleccionado
    else:
        return None


def guardar_cambios(entry_nombre, entry_apellido, entry_dni, entry_dias, lista_clientes, ventana_edicion):
    print("Guardando cambios...")
    if lista_clientes is None:
        messagebox.showerror("Error", "La lista de clientes no está disponible.")
        return

    cliente_seleccionado = obtener_cliente_seleccionado(lista_clientes)
    if cliente_seleccionado is None:
        messagebox.showerror("Error", "Selecciona un cliente para editar.")
        return
    dni_cliente_seleccionado = cliente_seleccionado.split(" - ")[1].split("DNI: ")[1]

    nuevos_datos = [
        entry_nombre.get(),
        entry_apellido.get(),
        entry_dni.get(),
        entry_dias.get()
    ]

    clientes = cargar_datos()

    for indice, cliente in enumerate(clientes):
        # Compara el DNI del cliente actual con el DNI del cliente seleccionado
        if cliente[1] == dni_cliente_seleccionado:
            # Extrae el número de días de la cadena y luego conviértelo en un entero
            nuevos_dias_str = nuevos_datos[3].split(' ')[0]
            nuevos_dias = int(nuevos_dias_str) if nuevos_dias_str.isdigit() else 0

            # Actualiza los datos del cliente
            clientes[indice] = [
                nuevos_datos[0],
                nuevos_datos[2],  # Cambia el DNI
                nuevos_datos[1],  # Cambia el apellido
                str(nuevos_dias),  # Actualiza los días restantes como cadena
            ]

            # Actualiza la lista de clientes
            lista_clientes.delete(indice)
            adeuda_dias = f"{nuevos_dias} días restantes" if nuevos_dias > 0 else "Al día"
            lista_clientes.insert(indice, f"NOMBRE: {nuevos_datos[0]} APELLIDO: {nuevos_datos[1]} - DNI: {nuevos_datos[2]} - {adeuda_dias}")

            guardar_datos(clientes)
            ventana_edicion.destroy()
            break

    guardar_datos(clientes)


def editar_cliente(clientes, lista_clientes):
    cliente_seleccionado = obtener_cliente_seleccionado(lista_clientes)
    print("Cliente seleccionado:", cliente_seleccionado)
    if cliente_seleccionado is None:
        messagebox.showerror("Error", "Selecciona un cliente para editar.")
        return

    ventana_edicion = tk.Toplevel()
    ventana_edicion.title("Editar Cliente")

    partes_cliente = cliente_seleccionado.split(" - ")
    nombre_apellido = partes_cliente[0].split("NOMBRE: ")[1]
    dni = partes_cliente[1].split("DNI: ")[1]
    dias_deseados = partes_cliente[2]

    nombre_actual, apellido_actual = nombre_apellido.split(" APELLIDO: ")
    
    ttk.Label(ventana_edicion, text="Nombre:").pack()
    entry_nombre = tk.Entry(ventana_edicion)
    entry_nombre.insert(0, nombre_actual)  
    entry_nombre.pack()

    ttk.Label(ventana_edicion, text="Apellido:").pack()
    entry_apellido = tk.Entry(ventana_edicion)
    entry_apellido.insert(0, apellido_actual) 
    entry_apellido.pack()

    ttk.Label(ventana_edicion, text="DNI:").pack()
    entry_dni = tk.Entry(ventana_edicion)
    entry_dni.insert(0, dni)  
    entry_dni.pack()

    ttk.Label(ventana_edicion, text="Días deseados:").pack()
    entry_dias = tk.Entry(ventana_edicion)
    entry_dias.insert(0, dias_deseados)  
    entry_dias.pack()

    boton_guardar = tk.Button(ventana_edicion, text="Guardar Cambios", command=lambda: guardar_cambios(entry_nombre, entry_apellido, entry_dni, entry_dias, lista_clientes, ventana_edicion))

    boton_guardar.pack()

    boton_cancelar = tk.Button(ventana_edicion, text="Cancelar", command=ventana_edicion.destroy)
    boton_cancelar.pack()

def ver_clientes():
    global lista_clientes  
    clientes = cargar_datos()
    if hasattr(ver_clientes, 'ventana_clientes') and ver_clientes.ventana_clientes.winfo_exists():
        ventana_clientes = ver_clientes.ventana_clientes
        ventana_clientes.title("Clientes")
    else:
        ventana_clientes = tk.Toplevel()
        ventana_clientes.title("Lista de Clientes")
        ver_clientes.ventana_clientes = ventana_clientes

    boton_editar_cliente = tk.Button(ventana_clientes, text="Editar Cliente", command=lambda: editar_cliente(clientes, lista_clientes))

    boton_eliminar_cliente = tk.Button(ventana_clientes, text="Eliminar Cliente", command=lambda: eliminar_cliente(obtener_cliente_seleccionado(lista_clientes), lista_clientes))
    
    boton_eliminar_cliente.pack(pady=10)

  

    boton_editar_cliente.pack(pady=10)

    ventana_clientes.configure(bg="black")  

    lista_clientes_label = tk.Label(ventana_clientes, text="Lista de Clientes", fg="white", bg="black", font=("Helvetica", 18, "bold"))
    lista_clientes_label.pack()

    lista_clientes = tk.Listbox(ventana_clientes, bg="black", fg="white", height=15, width=60, font=("Helvetica", 12))
    lista_clientes.pack()

    for cliente in clientes:
        nombre_cliente = cliente[0]
        dni_cliente = cliente[1]
        apellido_cliente = cliente[2]
        dias_restantes = int(cliente[3])
        adeuda_dias = f"{dias_restantes} días restantes" if dias_restantes > 0 else "Al día"
        lista_clientes.insert(tk.END, f"NOMBRE: {nombre_cliente} APELLIDO: {apellido_cliente} - DNI: {dni_cliente} - {adeuda_dias}")



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
        messagebox.showerror("NEW GYM -- DNI no encontrado", f"El DNI {dni_a_verificar} no se encuentra en la base de datos.")

def crear_interfaz():
    root = tk.Tk()
    root.title("NEW GYM - CONTROL MEMBRESÍA")
    root.geometry("600x600")
    root.configure(bg="black")

    cargar_datos()

    frame_main = tk.Frame(root, bg="black")
    frame_main.pack(expand=True, fill="both")

    logo_path = os.path.join("img", "logo_gimnasio.png")
    if os.path.exists(logo_path):
        logo_image = Image.open(logo_path)
        nuevo_ancho = 300
        nuevo_alto = 300
        logo_image = logo_image.resize((nuevo_ancho, nuevo_alto), Image.ANTIALIAS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(frame_main, image=logo_photo, bg="black")
        logo_label.image = logo_photo
        logo_label.pack(pady=10)

    frame_nuevo_cliente = tk.Frame(frame_main, bg="black", bd=3, relief=tk.RIDGE, padx=20, pady=20)
    frame_nuevo_cliente.pack(padx=10, pady=10, expand=True)

    ttk.Label(frame_nuevo_cliente, text="DNI", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_dni = tk.Entry(frame_nuevo_cliente, font=("Helvetica", 12))
    entry_dni.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(frame_nuevo_cliente, text="nombre", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_nombre = tk.Entry(frame_nuevo_cliente, font=("Helvetica", 12))
    entry_nombre.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(frame_nuevo_cliente, text="apellido", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_apellido = tk.Entry(frame_nuevo_cliente, font=("Helvetica", 12))
    entry_apellido.pack(fill=tk.X, padx=10, pady=10)

    button_frame = tk.Frame(frame_nuevo_cliente, bg="black")
    button_frame.pack(pady=10)

    boton_agregar_cliente = tk.Button(button_frame, text="agregar cliente", command=lambda: agregar_cliente(entry_dni, entry_nombre, entry_apellido, entry_dias))
    apply_button_style(boton_agregar_cliente)
    boton_agregar_cliente.pack(side=tk.LEFT, padx=10, pady=10)

    boton_ver_clientes = tk.Button(button_frame, text="ver / editar clientes", command=ver_clientes, bg="#96A6A4", fg="black", font=("Helvetica", 12, "bold"), relief=tk.RAISED)
    apply_button_style(boton_ver_clientes)
    boton_ver_clientes.pack(side=tk.LEFT, padx=10, pady=10)

    boton_verificar_dni = tk.Button(frame_main, text="verificar DNI", command=verificar_dni, bg="#96A6A4", fg="black", font=("Helvetica", 12, "bold"), relief=tk.RAISED)
    boton_verificar_dni.pack(pady=10)

    ttk.Label(frame_main, text="DNI a verificar", background="black", font=("Helvetica", 12), foreground="white").pack(pady=5)
    global entry_dni_a_verificar
    entry_dni_a_verificar = tk.Entry(frame_main, font=("Helvetica", 12))
    entry_dni_a_verificar.pack(pady=5)
    
    ttk.Label(frame_nuevo_cliente, text="días deseados", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_dias = tk.Entry(frame_nuevo_cliente, font=("Helvetica", 12))
    entry_dias.pack(fill=tk.X, padx=10, pady=10)

    button_frame = tk.Frame(frame_nuevo_cliente, bg="black")
    button_frame.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    restar_dia_global()
    crear_interfaz()