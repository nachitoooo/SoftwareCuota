import tkinter as tk
from tkinter import ttk, Scrollbar, messagebox, simpledialog
import os
from PIL import Image, ImageTk
import json
from customtkinter import *
import datetime

lista_clientes = None
ventana_clientes = None
ventana_edicion = None
clientes = []

def cargar_ultima_actualizacion():
    try:
        with open("ultima_actualizacion.txt", "r") as file:
            fecha_str = file.read()
            if fecha_str:
                return datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
    except FileNotFoundError:
        return None
    
def actualizar_deuda_dias(clientes):
    for cliente in clientes:
        dias_restantes = cliente["dias_restantes"]
        if dias_restantes <= 0:
            # Incrementar la deuda de días
            cliente["deuda_dias"] = cliente.get("deuda_dias", 0) + 1
            
def restar_dia_a_clientes(clientes, ultima_actualizacion):
    if ultima_actualizacion is not None:
        fecha_actual = datetime.datetime.now()
        diferencia = fecha_actual - ultima_actualizacion
        dias_pasados = diferencia.days

        if dias_pasados > 0:
            for cliente in clientes:
                dias_restantes = int(cliente["dias_restantes"])
                if dias_restantes > 0:
                    cliente["dias_restantes"] = max(dias_restantes - dias_pasados, 0)
                    
            actualizar_deuda_dias(clientes)
                    
def guardar_ultima_actualizacion():
    fecha_actual = datetime.datetime.now()
    with open("ultima_actualizacion.txt", "w") as file:
        file.write(fecha_actual.strftime("%Y-%m-%d"))
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
            nombre_cliente = (cliente["nombre"])
            apellido_cliente = (cliente["apellido"])
            if dias_restantes > 0:
                messagebox.showinfo("DNI Encontrado", f"El DNI {dni_a_verificar} corresponde con la base de datos. Nombre: {nombre_cliente}, Apellido: {apellido_cliente}. Quedan {dias_restantes} días.")
            else:
                messagebox.showinfo("DNI Encontrado", f"El DNI {dni_a_verificar} se encuentra en la base de datos. Está al día.")
            break
    if not dni_encontrado:
        messagebox.showerror("PURA VIDA -- DNI no encontrado", f"El DNI {dni_a_verificar} no se encuentra en la base de datos.")

def agregar_cliente(entry_dni, entry_nombre, entry_apellido, entry_dias, entry_monto_ingresado):
    monto = entry_monto_ingresado.get()
    dni = entry_dni.get()
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    dias = entry_dias.get()
    if dni and nombre and apellido and dias:
        try:
            monto = int(monto)  
        except ValueError:
            messagebox.showerror("Error. El monto ingresado no es válido.")
            return
        clientes = cargar_datos()
        nuevo_cliente = {
            "nombre": nombre,
            "dni": dni,
            "apellido": apellido,
            "dias_restantes": int(dias),
            "monto_ingresado": monto,
            "deuda_dias": 0  # Inicializar la deuda de días en 0
        }
        clientes.append(nuevo_cliente)
        guardar_datos(clientes)
        entry_dni.delete(0, tk.END)
        entry_nombre.delete(0, tk.END)
        entry_apellido.delete(0, tk.END)
        entry_dias.delete(0, tk.END)
        entry_monto_ingresado.delete(0, tk.END)

# Resto de tu código...

def obtener_cliente_seleccionado(lista_clientes):
    item_seleccionado = lista_clientes.selection()
    if item_seleccionado:
        cliente_seleccionado = lista_clientes.item(item_seleccionado[0])["values"]
        return cliente_seleccionado
    else:
        return None
    

def actualizar_lista_clientes():
    lista_clientes.delete(*lista_clientes.get_children())
    clientes = cargar_datos()

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

    if 0 <= cliente_index < len(clientes):
        nuevos_datos = [
            entry_nombre.get(),
            entry_apellido.get(),
            entry_dni.get(),
            entry_dias.get()
        ]

        clientes[cliente_index] = {
            "nombre": nuevos_datos[0],
            "dni": nuevos_datos[2],  
            "apellido": nuevos_datos[1],  
            "dias_restantes": int(nuevos_datos[3])
        }

        guardar_datos(clientes)
        ventana_edicion.destroy()
        actualizar_lista_clientes()

def editar_cliente():
    cliente_seleccionado = obtener_cliente_seleccionado(lista_clientes)
    if cliente_seleccionado:
        global ventana_edicion
        ventana_edicion = tk.Toplevel()
        ventana_edicion.title("Editar Cliente")
        fuente = ("Arial", 15)
        CTkLabel(ventana_edicion, text="Nombre:", text_color="black", width=350, font=fuente).pack()
        entry_nombre = CTkEntry(ventana_edicion, font=fuente)
        entry_nombre.insert(0, cliente_seleccionado[0])
        entry_nombre.pack()

        CTkLabel(ventana_edicion, text="Apellido:", text_color="black", width=350, font=fuente).pack()
        entry_apellido = CTkEntry(ventana_edicion, font=fuente)
        entry_apellido.insert(0, cliente_seleccionado[2])
        entry_apellido.pack()

        CTkLabel(ventana_edicion, text="DNI:", text_color="black", width=350, font=fuente).pack()
        entry_dni = CTkEntry(ventana_edicion, font=fuente)
        entry_dni.insert(0, cliente_seleccionado[1])
        entry_dni.pack()

        CTkLabel(ventana_edicion, text="Días Restantes:", text_color="black", width=350, font=fuente).pack()
        entry_dias = CTkEntry(ventana_edicion, font=fuente)
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

        tk.Frame(ventana_edicion, height=20).pack()
        saveIcon = CTkImage(Image.open("icon/save.png"))
        CTkButton(ventana_edicion, image=saveIcon,font=("Helvetica", 12, "bold"), text_color='black',corner_radius=25, fg_color="#FFA500", hover_color="#f57b01", text="Guardar Cambios", command=guardar_cambios).pack()
        
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

def buscar_cliente():
    consulta = label_buscar_cliente.get()
    if not lista_clientes:
        messagebox.showinfo("No hay clientes", "No hay clientes para buscar.")
        return

    for item in lista_clientes.get_children():
        values = lista_clientes.item(item, 'values')
        nombre_cliente = values[0]
        apellido_cliente = values[2]
        dni_cliente = values[1]
        if (consulta and consulta.lower() in nombre_cliente.lower()) or \
           (consulta and consulta.lower() in apellido_cliente.lower()) or \
           (consulta and consulta in dni_cliente):
            lista_clientes.selection_set(item)
        else:
            lista_clientes.selection_remove(item)

    if not lista_clientes.selection():
        messagebox.showinfo("Sin Resultados", "No se encontraron resultados para la búsqueda.")

def ver_clientes():
    global lista_clientes
    global ventana_clientes
    global label_buscar_cliente 
    
    if ventana_clientes is None or not ventana_clientes.winfo_exists():
        ventana_clientes = tk.Toplevel()
        ventana_clientes.title("Lista de Clientes")
        client_logo_path = "icon/client.ico"
        ventana_clientes.iconbitmap(client_logo_path)
        ventana_clientes.geometry("800x800")
        style = ttk.Style()
        style.configure("Title.TLabel", background="black", font=("Helvetica", 14), foreground="white")
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("TEntry", font=("Helvetica", 12))
        frame_busqueda = ttk.Frame(ventana_clientes)
        frame_busqueda.pack(pady=5, padx=5)

        searchIcon = CTkImage(Image.open("icon/search.png"))

        buttonSearch = CTkButton(frame_busqueda, text="Buscar cliente",font=("Helvetica", 12, "bold"), text_color='black', image=searchIcon, width=35, height=35, fg_color='#FFA500', hover_color="#f57b01", corner_radius=10, command=buscar_cliente)
        buttonSearch.grid(row=0, column=1, padx=10)

        label_buscar_cliente = CTkEntry(frame_busqueda, font=("Helvetica", 12), placeholder_text="Buscar por nombre, apellido o DNI.", justify="center", width=303)
        label_buscar_cliente.grid(row=0, column=0, padx=10)
        
        lista_clientes = ttk.Treeview(ventana_clientes, columns=("Nombre", "DNI", "Apellido", "Días Restantes", "Días Adeudados", "Monto Abonado"), show="headings")
        lista_clientes.heading("Nombre", text="Nombre")
        lista_clientes.heading("Apellido", text="Apellido")
        lista_clientes.heading("DNI", text="DNI")
        lista_clientes.heading("Días Restantes", text="Días Restantes")
        lista_clientes.heading("Días Adeudados", text="Días Adeudados")
        lista_clientes.heading("Monto Abonado", text="Monto Abonado")

        scroll_y = ttk.Scrollbar(ventana_clientes, orient="vertical", command=lista_clientes.yview)
        lista_clientes.configure(yscrollcommand=scroll_y.set)
        clientes = cargar_datos()
        if clientes:
            for cliente in clientes:
                dias_restantes = cliente["dias_restantes"]
                dias_adeudados = cliente.get("deuda_dias", 0)  # Obtener los días adeudados
                if dias_restantes <= 0:
                    lista_clientes.insert("", "end", values=(cliente["nombre"], cliente["dni"], cliente["apellido"], dias_restantes, dias_adeudados, cliente.get("monto_ingresado", 0.0)), tags=('rojo',))
                else:
                    lista_clientes.insert("", "end", values=(cliente["nombre"], cliente["dni"], cliente["apellido"], dias_restantes, "No adeuda dias.", cliente.get("monto_ingresado", 0.0)))

        lista_clientes.tag_configure('rojo', background='#ff5757')

        frame_botones = ttk.Frame(ventana_clientes)
        frame_botones.pack(pady=10)
        
        pencilIcon = CTkImage(Image.open("icon/pencil.png"))
        boton_editar = CTkButton(frame_botones, text="Editar Cliente", font=("Helvetica", 12, "bold"), fg_color="#FFA500", hover_color="#f57b01", text_color="black", command=editar_cliente, image=pencilIcon, corner_radius=10)
        boton_editar.grid(row=0, column=0, padx=10)

        deleteIcon = CTkImage(Image.open("icon/delete.png"))
        boton_eliminar = CTkButton(frame_botones, text="Eliminar Cliente", font=("Helvetica", 12, "bold"), fg_color="#FFA500",hover_color="#f57b01", text_color="black", image=deleteIcon, corner_radius=10, command=lambda: eliminar_cliente(lista_clientes))
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

def toggle_fullscreen(event, root):
    root.attributes('-fullscreen', not root.attributes('-fullscreen'))

def crear_interfaz():
    root = CTk()
    root.title("Pura vida - Software de control de Cuota de clientes.")
    imagen = "icon/gymlogo.ico"
    root.iconbitmap(imagen)
    
    root.attributes('-fullscreen', True)
    root.bind("<F11>", lambda event: toggle_fullscreen(event, root))

    frame_main = tk.Frame(root, bg="black")
    frame_main.pack(expand=True, fill="both")
    logo_path = os.path.join("icon", "logo.png")
    if os.path.exists(logo_path):
        logo_image = Image.open(logo_path)
        nuevo_ancho = 500
        nuevo_alto = 300
        logo_image = logo_image.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(frame_main, image=logo_photo, bg="black")
        logo_label.image = logo_photo
        logo_label.pack(pady=0)

    frame_nuevo_cliente = tk.Frame(frame_main, bg="black", bd=1.4, relief=tk.RIDGE, padx=10, pady=10)
    frame_nuevo_cliente.pack(padx=10, pady=10, expand=True)
    frame_nuevo_cliente.configure(padx=5, pady=5)

    ttk.Label(frame_nuevo_cliente, text="DNI", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_dni = CTkEntry(frame_nuevo_cliente, font=("Arial", 12), bg_color="black", fg_color="black", corner_radius=10, placeholder_text="Ingrese DNI", justify="center")
    entry_dni.pack(fill=tk.X, padx=5, pady=5)

    ttk.Label(frame_nuevo_cliente, text="Nombre", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_nombre = CTkEntry(frame_nuevo_cliente, font=("Arial", 12), bg_color="black", fg_color="black", corner_radius=10, placeholder_text="Ingrese nombre", justify="center")
    entry_nombre.pack(fill=tk.X, padx=5, pady=5)

    ttk.Label(frame_nuevo_cliente, text="Apellido", background="black", font=("Helvetica", 12), foreground="white").pack()
    entry_apellido = CTkEntry(frame_nuevo_cliente, font=("Arial", 12), bg_color="black", fg_color="black", corner_radius=10, placeholder_text="Ingrese apellido", justify="center")
    entry_apellido.pack(fill=tk.X, padx=5, pady=5)
    button_frame = tk.Frame(frame_nuevo_cliente, bg="black")
    button_frame.pack(pady=5)

    boton_agregar_cliente = CTkButton(
        button_frame,
        text="Agregar Cliente",
        corner_radius=25,
        text_color="black",
        fg_color="#FFA500",
        font=("Helvetica", 14, "bold"),
        command=lambda: agregar_cliente(entry_dni, entry_nombre, entry_apellido, entry_dias, entry_monto_ingresado)
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

    verify_dni_Img = CTkImage(Image.open("icon/icons8-verify-30.png"))
    boton_verificar_dni = CTkButton(frame_main, text="Verificar DNI", image=verify_dni_Img, fg_color="#FFA500", hover_color=("#f57b01"), command=verificar_dni, corner_radius=25, text_color="black", font=("Helvetica", 12, "bold"))
    boton_verificar_dni.pack(pady=10)
    
    global entry_dni_a_verificar
    entry_dni_a_verificar = CTkEntry(frame_main, font=("Helvetica", 12), placeholder_text="Ingrese DNI a verificar.", width=200, corner_radius=13, justify="center")
    entry_dni_a_verificar.pack(pady=5)

    ttk.Label(frame_nuevo_cliente, text="Días Abonados", background="black", font=("Arial", 12), foreground="white").pack()
    entry_dias = CTkEntry(frame_nuevo_cliente, font=("Helvetica", 12), fg_color="black", corner_radius=10, placeholder_text="Ingrese días", justify="center")
    entry_dias.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(frame_nuevo_cliente, text="Monto Abonado", background="black", font=("Arial", 12), foreground="white").pack()
    entry_monto_ingresado = CTkEntry(frame_nuevo_cliente, font=("Helvetica", 12), fg_color="black", corner_radius=10, placeholder_text="Ingrese monto", justify="center")
    entry_monto_ingresado.pack(fill=tk.X, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    cargar_datos()
    clientes = cargar_datos()
    ultima_actualizacion = cargar_ultima_actualizacion
    if ultima_actualizacion:
        ultima_actualizacion = ultima_actualizacion() 
        restar_dia_a_clientes(clientes, ultima_actualizacion)
    guardar_datos(clientes)
    guardar_ultima_actualizacion()
    crear_interfaz()