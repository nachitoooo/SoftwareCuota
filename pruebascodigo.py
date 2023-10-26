import tkinter as tk
from tkinter import ttk, Scrollbar, messagebox, simpledialog
import os
from PIL import Image, ImageTk
import json
from customtkinter import *
from customtkinter import CTkEntry, CTkButton



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
            clientes.remove(clientes[lista_clientes.index(item_seleccionado[0])])
            guardar_datos(clientes)  
            lista_clientes.delete(item_seleccionado)
def buscar_cliente(nombre, apellido, dni):
    if not lista_clientes:
        messagebox.showinfo("No hay clientes", "No hay clientes para buscar.")
        return

    for item in lista_clientes.get_children():
        values = lista_clientes.item(item, 'values')
        nombre_cliente = values[0]
        apellido_cliente = values[2]
        dni_cliente = values[1]

        if (nombre and nombre.lower() in nombre_cliente.lower()) or \
           (apellido and apellido.lower() in apellido_cliente.lower()) or \
           (dni and dni in dni_cliente):
            lista_clientes.selection_set(item)
        else:
            lista_clientes.selection_remove(item)

    if not lista_clientes.selection():
        messagebox.showinfo("Sin Resultados", "No se encontraron resultados para la búsqueda.")


def ver_clientes():
    global lista_clientes
    global ventana_clientes

    if ventana_clientes is None or not ventana_clientes.winfo_exists():
        ventana_clientes = tk.Toplevel()
        ventana_clientes.title("Lista de Clientes")
        ventana_clientes.geometry("800x800")

        style = ttk.Style()
        style.configure("Title.TLabel", background="black", font=("Helvetica", 14), foreground="white")
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("TEntry", font=("Helvetica", 12))

        ttk.Label(ventana_clientes, text="Buscar Cliente", style="Title.TLabel").pack(pady=10)

        frame_busqueda = ttk.Frame(ventana_clientes)
        frame_busqueda.pack(pady=10, padx=10)

        ttk.Label(frame_busqueda, text="Nombre").grid(row=0, column=0, padx=10, pady=5)
        entry_buscar_nombre = ttk.Entry(frame_busqueda)
        entry_buscar_nombre.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame_busqueda, text="Apellido").grid(row=1, column=0, padx=10, pady=5)
        entry_buscar_apellido = ttk.Entry(frame_busqueda)
        entry_buscar_apellido.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(frame_busqueda, text="DNI").grid(row=2, column=0, padx=10, pady=5)
        entry_buscar_dni = ttk.Entry(frame_busqueda)
        entry_buscar_dni.grid(row=2, column=1, padx=10, pady=5)

        boton_buscar_cliente = CTkButton(frame_busqueda, text="Buscar Cliente", corner_radius=25, fg_color="#edb605", command=lambda: buscar_cliente(entry_buscar_nombre.get(), entry_buscar_apellido.get(), entry_buscar_dni.get()))
        boton_buscar_cliente.grid(row=3, columnspan=2, pady=10)
 

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

        frame_botones = ttk.Frame(ventana_clientes)
        frame_botones.pack(pady=10)

        boton_editar = ttk.Button(frame_botones, text="Editar Cliente", command=editar_cliente)
        boton_editar.grid(row=0, column=0, padx=10)

        boton_eliminar = ttk.Button(frame_botones, text="Eliminar Cliente", command=lambda: eliminar_cliente(lista_clientes))
        boton_eliminar.grid(row=0, column=1, padx=10)

        lista_clientes.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")


def guardar_datos(clientes):
    try:
        with open("clientes.json", "w+") as file:
            json.dump(clientes, file, indent=4)
    except FileExistsError:
        with open("clientes.json", "w") as file:
            json.dump(clientes, file, indent=4)



def crear_interfaz():
    root = CTk()
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
        logo_image = logo_image.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(frame_main, image=logo_photo, bg="black")
        logo_label.image = logo_photo
        logo_label.pack(pady=10)

    frame_nuevo_cliente = tk.Frame(frame_main, bg="black", bd=3, relief=tk.RIDGE, padx=20, pady=20)
    frame_nuevo_cliente.pack(padx=10, pady=10, expand=True)

    ttk.Label(frame_nuevo_cliente, text="DNI", background="black", font=("Helvetica", 12), foreground="white").pack()

    entry_dni = CTkEntry(frame_nuevo_cliente, font=("Helvetica", 12), bg_color="white", fg_color="black")
    entry_dni.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(frame_nuevo_cliente, text="Nombre", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_nombre = CTkEntry(frame_nuevo_cliente, font=("Helvetica", 12), bg_color="white", fg_color="black")
    entry_nombre.pack(fill=tk.X, padx=10, pady=10)    

    ttk.Label(frame_nuevo_cliente, text="Apellido", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_apellido = CTkEntry(frame_nuevo_cliente, font=("Helvetica", 12), bg_color="white", fg_color="black")
    entry_apellido.pack(fill=tk.X, padx=10, pady=10)
    

    button_frame = tk.Frame(frame_nuevo_cliente, bg="black")
    button_frame.pack(pady=10)

    boton_agregar_cliente = CTkButton(
    button_frame, 
    text="Agregar Cliente",
    corner_radius=25,
    text_color="black",
    fg_color="#FFA500",
    font=("Helvetica", 14, "bold"),  
    command=lambda: agregar_cliente(entry_dni, entry_nombre, entry_apellido, entry_dias)
    )

    boton_agregar_cliente.pack(side=tk.LEFT, padx=10, pady=10)
    boton_agregar_cliente.configure(hover_color="#f57b01")

     
    boton_ver_clientes = CTkButton(
    button_frame, 
    text="Gestionar Clientes",
    corner_radius=25,
    fg_color="#FFA500",
    text_color="black",
    font=("Helvetica", 14, "bold"),  
    command=ver_clientes
)
    boton_ver_clientes.pack(side=tk.LEFT, padx=10, pady=10)
    boton_ver_clientes.configure(hover_color="#f57b01")

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