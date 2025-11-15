import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ----------------------------------------------------------------------
# --- 1. CONFIGURACIÓN DE LA BASE DE DATOS ---
# ----------------------------------------------------------------------
DB_CONFIG = {
    'host': 'localhost',
    'database': 'camaleonides',
    'user': '****',  #Usuario del hostlocal
    'password': '*********'  # Contraseña de hostlocal
}

# ----------------------------------------------------------------------
# --- 2. MODELO BASE ---
# ----------------------------------------------------------------------
class ModeloBase:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None
        self.conectar_db()

    def conectar_db(self):
        try:
            if self.conn is None or not self.conn.is_connected():
                self.conn = mysql.connector.connect(**self.config)
                self.cursor = self.conn.cursor()
                print("Conexión a MySQL establecida.")
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar:\n{err}")
            return False

    def ejecutar_query(self, query, params=None, fetch=True):
        if not self.conectar_db():
            return [] if fetch else False
        try:
            self.cursor.execute(query, params or ())
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.conn.commit()
                return True
            return self.cursor.fetchall() if fetch else True
        except mysql.connector.Error as err:
            messagebox.showerror("Error SQL", f"{err.errno} - {err.msg}")
            self.conn.rollback()
            return [] if fetch else False

# ----------------------------------------------------------------------
# --- MODELOS ESPECÍFICOS ---
# ----------------------------------------------------------------------
class ModeloUsuarios(ModeloBase):
    def obtener_todos(self):
        query = "SELECT id_usuario, nombre, apellido_paterno, usuario, rango FROM usuarios"
        return self.ejecutar_query(query)

    def insertar(self, nombre, apellido_p, usuario, contraseña, rango):
        query = "INSERT INTO usuarios (nombre, apellido_paterno, usuario, contraseña, rango) VALUES (%s, %s, %s, %s, %s)"
        return self.ejecutar_query(query, (nombre, apellido_p, usuario, contraseña, rango), fetch=False)

    def actualizar(self, id_usuario, nombre, apellido_p, usuario, contraseña, rango):
        query = "UPDATE usuarios SET nombre=%s, apellido_paterno=%s, usuario=%s, contraseña=%s, rango=%s WHERE id_usuario=%s"
        return self.ejecutar_query(query, (nombre, apellido_p, usuario, contraseña, rango, id_usuario), fetch=False)

    def eliminar(self, id_usuario):
        query = "DELETE FROM usuarios WHERE id_usuario=%s"
        return self.ejecutar_query(query, (id_usuario,), fetch=False)

class ModeloAlimentos(ModeloBase):
    def obtener_todos(self):
        query = "SELECT id_alimento, nombre, stock_kg, fecha_compra FROM alimentos"
        return self.ejecutar_query(query)

    def actualizar_stock(self, id_alimento, nuevo_stock):
        query = "UPDATE alimentos SET stock_kg=%s WHERE id_alimento=%s"
        return self.ejecutar_query(query, (nuevo_stock, id_alimento), fetch=False)

class ModeloInsectos(ModeloBase):
    def obtener_todos(self):
        query = """
            SELECT 'Grillos' as especie, id_insecto, stock, etapa FROM insectos_grillos
            UNION ALL SELECT 'Cucarachas', id_insecto, stock, etapa FROM insectos_cucarachas
            UNION ALL SELECT 'Zophobas', id_insecto, stock, etapa FROM insectos_zophobas
            UNION ALL SELECT 'Tenebrios', id_insecto, stock, etapa FROM insectos_tenebrios
        """
        return self.ejecutar_query(query)

    def restar_stock(self, especie, cantidad):
        tabla = f"insectos_{especie}s" if especie != "tenebrio" else "insectos_tenebrios"
        query = f"UPDATE {tabla} SET stock = stock - %s WHERE id_insecto = 1"
        return self.ejecutar_query(query, (cantidad,), fetch=False)

class ModeloVentas(ModeloBase):
    def obtener_todos(self):
        query = """
            SELECT id_venta, especie, cantidad, etapa, fecha_salida, estado 
            FROM ventas ORDER BY fecha_salida DESC
        """
        return self.ejecutar_query(query)

    def registrar_venta(self, especie, cantidad, etapa):
        # Insertar venta
        query_venta = """
            INSERT INTO ventas (id_insecto, especie, cantidad, etapa, fecha_salida, id_usuario)
            VALUES (1, %s, %s, %s, CURDATE(), 1)
        """
        # Restar stock
        modelo_insectos = ModeloInsectos(DB_CONFIG)
        if modelo_insectos.restar_stock(especie, cantidad):
            return self.ejecutar_query(query_venta, (especie, cantidad, etapa), fetch=False)
        return False

# ----------------------------------------------------------------------
# --- VISTA BASE ---
# ----------------------------------------------------------------------
class VistaTablaBase:
    def __init__(self, master, modelo, nombre_tabla, columnas):
        self.master = master
        self.modelo = modelo
        self.nombre_tabla = nombre_tabla
        self.columnas = columnas
        self.create_widgets()
        self.cargar_todos()

    def create_widgets(self):
        control_frame = ttk.Frame(self.master, padding="10")
        control_frame.pack(fill='x')

        ttk.Label(control_frame, text=f"Buscar en {self.nombre_tabla}:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(control_frame, width=20)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(control_frame, text="Buscar", command=self.buscar).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Cargar Todos", command=self.cargar_todos).pack(side='left', padx=10)

        table_frame = ttk.Frame(self.master, padding="10")
        table_frame.pack(expand=True, fill='both')
        self.create_treeview(table_frame)

    def create_treeview(self, frame):
        cols = list(self.columnas.keys())
        self.tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=self.columnas[col])
            self.tree.column(col, width=120)
        self.tree.pack(expand=True, fill='both')
        self.tree.bind('<Double-1>', lambda e: self.editar_seleccionado())

    def poblar_tabla(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in data:
            self.tree.insert('', 'end', values=row)

    def cargar_todos(self):
        data = self.modelo.obtener_todos()
        self.poblar_tabla(data)

    def buscar(self):
        term = self.search_entry.get()
        # Búsqueda básica por nombre
        query = f"SELECT * FROM {self.nombre_tabla.lower()} WHERE nombre LIKE %s"
        data = self.modelo.ejecutar_query(query, (f"%{term}%",))
        self.poblar_tabla(data)

    def obtener_seleccionado(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Advertencia", "Selecciona un registro.")
            return None
        return self.tree.item(sel, 'values')[0]  # ID

    def editar_seleccionado(self):
        pass  # Implementar en hijas

# ----------------------------------------------------------------------
# --- VISTAS ESPECÍFICAS ---
# ----------------------------------------------------------------------
class VistaUsuarios(VistaTablaBase):
    def __init__(self, master, modelo):
        columnas = {'ID': 'ID', 'Nombre': 'Nombre', 'Apellido': 'Apellido', 'Usuario': 'Usuario', 'Rango': 'Rango'}
        super().__init__(master, modelo, "usuarios", columnas)

    def editar_seleccionado(self):
        id_usuario = self.obtener_seleccionado()
        if id_usuario:
            win = tk.Toplevel()
            win.title("Editar Usuario")
            entries = {}
            fields = ['Nombre', 'Apellido', 'Usuario', 'Contraseña', 'Rango']
            for i, f in enumerate(fields):
                ttk.Label(win, text=f"{f}:").grid(row=i, column=0, padx=5, pady=5)
                entry = ttk.Entry(win)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries[f] = entry

            data = self.modelo.ejecutar_query("SELECT nombre, apellido_paterno, usuario, contraseña, rango FROM usuarios WHERE id_usuario=%s", (id_usuario,))[0]
            for i, val in enumerate(data):
                entries[fields[i]].insert(0, val)

            def guardar():
                vals = [entries[f].get() for f in fields]
                if self.modelo.actualizar(id_usuario, *vals):
                    messagebox.showinfo("Éxito", "Usuario actualizado.")
                    win.destroy()
                    self.cargar_todos()
            ttk.Button(win, text="Guardar", command=guardar).grid(row=5, column=1, pady=10)

class VistaAlimentosInsectos(VistaTablaBase):
    def __init__(self, master, modelo_ali, modelo_ins):
        self.modelo_ali = modelo_ali
        self.modelo_ins = modelo_ins
        columnas = {'Especie': 'Especie', 'ID': 'ID', 'Stock': 'Stock', 'Etapa': 'Etapa'}
        super().__init__(master, modelo_ins, "insectos", columnas)

    def create_control_buttons(self, frame):
        super().create_control_buttons(frame)
        ttk.Button(frame, text="+10kg Calabaza", command=self.sumar_calabaza).pack(side='right', padx=5)

    def sumar_calabaza(self):
        if self.modelo_ali.actualizar_stock(1, "stock_kg + 10"):
            messagebox.showinfo("Éxito", "+10kg calabaza")
            self.cargar_todos()

class VistaVentas(VistaTablaBase):
    def __init__(self, master, modelo_ventas, modelo_insectos):
        self.modelo_ventas = modelo_ventas
        self.modelo_insectos = modelo_insectos
        columnas = {'ID': 'ID', 'Especie': 'Especie', 'Cantidad': 'Cantidad', 'Etapa': 'Etapa', 'Fecha': 'Fecha', 'Estado': 'Estado'}
        super().__init__(master, modelo_ventas, "ventas", columnas)

    def create_control_buttons(self, frame):
        super().create_control_buttons(frame)
        ttk.Button(frame, text="Registrar Venta", command=self.registrar_venta).pack(side='right', padx=5)

    def registrar_venta(self):
        win = tk.Toplevel()
        win.title("Nueva Venta a Petco")
        ttk.Label(win, text="Especie:").grid(row=0, column=0)
        especie = ttk.Combobox(win, values=["grillo", "cucaracha", "zophobas", "tenebrio"])
        especie.grid(row=0, column=1)
        ttk.Label(win, text="Cantidad:").grid(row=1, column=0)
        cant = ttk.Entry(win)
        cant.grid(row=1, column=1)

        def vender():
            try:
                c = int(cant.get())
                esp = especie.get()
                if self.modelo_ventas.registrar_venta(esp, c, 'adulto'):
                    messagebox.showinfo("Éxito", f"Venta de {c} {esp}s registrada.")
                    win.destroy()
                    self.cargar_todos()
            except:
                messagebox.showerror("Error", "Cantidad inválida.")

        ttk.Button(win, text="Vender", command=vender).grid(row=2, column=1, pady=10)

# ----------------------------------------------------------------------
# --- APLICACIÓN PRINCIPAL ---
# ----------------------------------------------------------------------
class AppCamaleonides(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAMALEONIDES - Cría y Ventas")
        self.geometry("1000x600")

        self.modelos = {
            'usuarios': ModeloUsuarios(DB_CONFIG),
            'alimentos': ModeloAlimentos(DB_CONFIG),
            'insectos': ModeloInsectos(DB_CONFIG),
            'ventas': ModeloVentas(DB_CONFIG)
        }

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Pestañas
        frame_usu = ttk.Frame(notebook)
        notebook.add(frame_usu, text='Usuarios')
        VistaUsuarios(frame_usu, self.modelos['usuarios'])

        frame_inv = ttk.Frame(notebook)
        notebook.add(frame_inv, text='Inventario')
        VistaAlimentosInsectos(frame_inv, self.modelos['alimentos'], self.modelos['insectos'])

        frame_ven = ttk.Frame(notebook)
        notebook.add(frame_ven, text='Ventas')
        VistaVentas(frame_ven, self.modelos['ventas'], self.modelos['insectos'])

if __name__ == "__main__":
    app = AppCamaleonides()
    app.mainloop()
