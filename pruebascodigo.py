import tkinter as tk
from tkinter import ttk, Scrollbar, messagebox, simpledialog
import os
from PIL import Image, ImageTk
import json
import re


lista_clientes = None
ventana_clientes = None
ventana_edicion = None

clientes = []

def cargar_datos():
    global clientes
    try:
        with open("clientes.json", "r") as file:
            clientes = json.load(file)
        return clientes
    except FileNotFoundError:
        return []

def verificar_dni():
    dni_a_verificar = entry_dni_a_verificar.get()

    clientes = cargar_datos()

    dni_encontrado = False
    for cliente in clientes:
        if cliente["dni"] == dni_a_verificar:
            dni_encontrado = True
            dias_restantes = int(cliente["dias_restantes"])
            if dias_restantes > 0:
                messagebox.showinfo("DNI Encontrado", f"El DNI {dni_a_verificar} se encuentra en la base de datos. Quedan {dias_restantes} días.")
            else:
                messagebox.showinfo("DNI Encontrado", f"El DNI {dni_a_verificar} se encuentra en la base de datos. Está al día.")
            break

    if not dni_encontrado:
        messagebox.showerror("NEW GYM -- DNI no encontrado", f"El DNI {dni_a_verificar} no se encuentra en la base de datos.")

def agregar_cliente(entry_dni, entry_nombre, entry_apellido, entry_dias):
    dni = entry_dni.get()
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    dias = entry_dias.get()

    if dni and nombre and apellido and dias:
        clientes = cargar_datos()
        nuevo_cliente = {"nombre": nombre, "dni": dni, "apellido": apellido, "dias_restantes": int(dias)}
        clientes.append(nuevo_cliente)
        guardar_datos(clientes)

        entry_dni.delete(0, tk.END)
        entry_nombre.delete(0, tk.END)
        entry_apellido.delete(0, tk.END)
        entry_dias.delete(0, tk.END)

def obtener_cliente_seleccionado(lista_clientes):
    item_seleccionado = lista_clientes.selection()
    if item_seleccionado:
        cliente_seleccionado = lista_clientes.item(item_seleccionado[0])["values"]
        return cliente_seleccionado
    else:
        return None
    



def actualizar_lista_clientes():
    lista_clientes.delete(*lista_clientes.get_children())  # Borrar todos los elementos de la lista
    clientes = cargar_datos()  # Cargar la lista de clientes actualizada
    for cliente in clientes:
        lista_clientes.insert("", "end", values=(cliente["nombre"], cliente["dni"], cliente["apellido"], cliente["dias_restantes"]))


def guardar_cambios(entry_nombre, entry_apellido, entry_dni, entry_dias, lista_clientes, dni_anterior):
    global clientes
    if lista_clientes is None:
        messagebox.showerror("Error", "La lista de clientes no está disponible.")
        return

    item_seleccionado = lista_clientes.selection()
    if not item_seleccionado:
        messagebox.showerror("Error", "Selecciona un cliente para editar.")
        return

    cliente_index = lista_clientes.index(item_seleccionado)
    
    # Verifica si el índice es válido
    if 0 <= cliente_index < len(clientes):
        nuevos_datos = [
            entry_nombre.get(),
            entry_apellido.get(),
            entry_dni.get(),
            entry_dias.get()
        ]

        # Actualiza los datos del cliente en la lista
        clientes[cliente_index] = {
            "nombre": nuevos_datos[0],
            "dni": nuevos_datos[2],  # Modifica el DNI
            "apellido": nuevos_datos[1],  # Modifica el apellido
            "dias_restantes": int(nuevos_datos[3])
        }

        # Guarda la lista actualizada en el archivo JSON
        guardar_datos(clientes)
        ventana_edicion.destroy()
        actualizar_lista_clientes()


def editar_cliente():
    cliente_seleccionado = obtener_cliente_seleccionado(lista_clientes)
    if cliente_seleccionado:
        global ventana_edicion
        ventana_edicion = tk.Toplevel()
        ventana_edicion.title("Editar Cliente")
        
        ttk.Label(ventana_edicion, text="Nombre:").pack()
        entry_nombre = ttk.Entry(ventana_edicion)
        entry_nombre.insert(0, cliente_seleccionado[0])
        entry_nombre.pack()
        
        ttk.Label(ventana_edicion, text="Apellido:").pack()
        entry_apellido = ttk.Entry(ventana_edicion)
        entry_apellido.insert(0, cliente_seleccionado[2])
        entry_apellido.pack()
        
        ttk.Label(ventana_edicion, text="DNI:").pack()
        entry_dni = ttk.Entry(ventana_edicion)
        entry_dni.insert(0, cliente_seleccionado[1])
        entry_dni.pack()
        
        ttk.Label(ventana_edicion, text="Días Restantes:").pack()
        entry_dias = ttk.Entry(ventana_edicion)
        entry_dias.insert(0, cliente_seleccionado[3])
        entry_dias.pack()
        
        def guardar_cambios():
            nuevos_datos = [
                entry_nombre.get(),
                entry_dni.get(),
                entry_apellido.get(),
                entry_dias.get()
            ]

            if '' in nuevos_datos:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
            else:
                global clientes
                if lista_clientes:
                    item_seleccionado = lista_clientes.selection()
                    if item_seleccionado:
                        cliente_index = lista_clientes.index(item_seleccionado[0])
                        if cliente_index is not None and 0 <= cliente_index < len(clientes):
                            clientes[cliente_index] = {
                                "nombre": nuevos_datos[0],
                                "dni": nuevos_datos[1],
                                "apellido": nuevos_datos[2],
                                "dias_restantes": int(nuevos_datos[3])
                            }
                            guardar_datos(clientes)
                            ventana_edicion.destroy()
                            actualizar_lista_clientes()

        ttk.Button(ventana_edicion, text="Guardar Cambios", command=guardar_cambios).pack()
        
def eliminar_cliente(lista_clientes):
    item_seleccionado = lista_clientes.selection()
    if item_seleccionado:
        result = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este cliente?")
        if result:
            dni_cliente = lista_clientes.item(item_seleccionado[0])["values"][1]
            clientes = cargar_datos()
            clientes = [cliente for cliente in clientes if cliente["dni"] != dni_cliente]
            guardar_datos(clientes)
            lista_clientes.delete(item_seleccionado)

def ver_clientes():
    global lista_clientes
    global ventana_clientes

    if ventana_clientes is None or not ventana_clientes.winfo_exists():
        ventana_clientes = tk.Toplevel()
        ventana_clientes.title("Lista de Clientes")
        ventana_clientes.geometry("800x800")

        lista_clientes = ttk.Treeview(ventana_clientes, columns=("Nombre", "DNI", "Apellido", "Días Restantes"), show="headings")
        lista_clientes.heading("Nombre", text="Nombre")
        lista_clientes.heading("Apellido", text="Apellido")
        lista_clientes.heading("DNI", text="DNI")
        lista_clientes.heading("Días Restantes", text="Días Restantes")

        scroll_y = ttk.Scrollbar(ventana_clientes, orient="vertical", command=lista_clientes.yview)
        lista_clientes.configure(yscrollcommand=scroll_y.set)

        clientes = cargar_datos()

        if clientes:
            for cliente in clientes:
                lista_clientes.insert("", "end", values=(cliente["nombre"], cliente["dni"], cliente["apellido"], cliente["dias_restantes"]))

        boton_editar = tk.Button(ventana_clientes, text="Editar Cliente", command=editar_cliente)


        boton_eliminar = tk.Button(ventana_clientes, text="Eliminar cliente", command=lambda: eliminar_cliente(lista_clientes))

        lista_clientes.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        boton_editar.pack()
        boton_eliminar.pack()

    ventana_clientes.focus_force()

def guardar_datos(clientes):
    try:
        with open("clientes.json", "w+") as file:
            json.dump(clientes, file, indent=4)
    except FileExistsError:
        with open("clientes.json", "w") as file:
            json.dump(clientes, file, indent=4)




def crear_interfaz():
    root = tk.Tk()
    root.title("NEW GYM - CONTROL MEMBRESÍA")
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.configure(bg="black")

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

    boton_agregar_cliente = tk.Button(
    button_frame, text="Agregar Cliente", command=lambda: agregar_cliente(entry_dni, entry_nombre, entry_apellido, entry_dias))
    boton_agregar_cliente.pack(side=tk.LEFT, padx=10, pady=10)

    boton_ver_clientes = tk.Button(button_frame, text="ver / editar clientes", command=ver_clientes, bg="#96A6A4", fg="black", font=("Helvetica", 12, "bold"), relief=tk.RAISED)
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
    cargar_datos()
    crear_interfaz()
