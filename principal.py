import tkinter as tk
from tkinter import ttk

class FigurasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Figuras con Flechas")
        self.root.geometry("900x650")
        
        # Variables
        self.figura_seleccionada = tk.StringVar(value="rectangulo")
        self.modo_conexion = False
        self.conexion_iniciada = False
        self.elemento_origen = None
        self.color_relleno = "lightblue"
        self.color_flecha = "black"
        
        # Crear paneles
        self.crear_panel_izquierdo()
        self.crear_panel_derecho()
        
        # Configurar eventos
        self.canvas.bind("<Button-1>", self.manejar_clic)
        self.canvas.bind("<Motion>", self.manejar_movimiento)
        
        # Almacén de elementos y conexiones
        self.elementos = []
        self.conexiones = []
    
    def crear_panel_izquierdo(self):
        # Frame para el panel de herramientas
        panel = ttk.Frame(self.root, width=220, padding=10)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)
        
        # Título
        ttk.Label(panel, text="Herramientas", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Sección de figuras
        ttk.Label(panel, text="Crear Figuras:").pack(anchor="w", pady=(10,0))
        
        figuras = [
            ("Rectángulo", "rectangulo"),
            ("Óvalo", "ovalo"),
            ("Rombo", "rombo")
        ]
        
        for texto, valor in figuras:
            rb = ttk.Radiobutton(
                panel, 
                text=texto,
                variable=self.figura_seleccionada,
                value=valor
            )
            rb.pack(anchor="w", pady=2)
        
        # Separador
        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=15)
        
        # Sección de conexiones
        ttk.Label(panel, text="Conectar Elementos:").pack(anchor="w", pady=(5,0))
        
        self.btn_conectar = ttk.Button(
            panel, 
            text="Modo Conexión", 
            command=self.toggle_modo_conexion
        )
        self.btn_conectar.pack(fill="x", pady=5)
        
        # Separador
        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=15)
        
        # Botón para limpiar
        ttk.Button(panel, text="Limpiar Todo", command=self.limpiar_canvas).pack(fill="x", pady=10)
    
    def crear_panel_derecho(self):
        # Frame para el área de dibujo
        frame_dibujo = ttk.Frame(self.root, padding=5)
        frame_dibujo.pack(side="right", expand=True, fill="both")
        
        # Canvas para dibujar
        self.canvas = tk.Canvas(frame_dibujo, bg="white", bd=2, relief="ridge")
        self.canvas.pack(expand=True, fill="both")
        
        # Texto de ayuda
        self.texto_ayuda = self.canvas.create_text(
            10, 10, 
            anchor="nw",
            text="Selecciona una figura y haz clic en el área para crearla",
            fill="gray50"
        )
    
    def toggle_modo_conexion(self):
        self.modo_conexion = not self.modo_conexion
        if self.modo_conexion:
            self.btn_conectar.config(text="Salir Modo Conexión")
            self.actualizar_texto_ayuda("Modo conexión: Haz clic en el primer elemento a conectar")
        else:
            self.btn_conectar.config(text="Modo Conexión")
            self.actualizar_texto_ayuda("Selecciona una figura y haz clic en el área para crearla")
            self.conexion_iniciada = False
            self.elemento_origen = None
    
    def actualizar_texto_ayuda(self, mensaje):
        self.canvas.itemconfig(self.texto_ayuda, text=mensaje)
    
    def manejar_clic(self, event):
        if self.modo_conexion:
            self.procesar_conexion(event)
        else:
            self.crear_figura(event)
    
    def procesar_conexion(self, event):
        # Buscar el elemento más cercano al clic
        item = self.canvas.find_closest(event.x, event.y)
        
        if item and item[0] != self.texto_ayuda:  # Ignorar el texto de ayuda
            if not self.conexion_iniciada:
                # Primer elemento de la conexión
                self.elemento_origen = item[0]
                self.conexion_iniciada = True
                self.actualizar_texto_ayuda("Modo conexión: Ahora haz clic en el segundo elemento")
                self.canvas.itemconfig(self.elemento_origen, outline="red", width=2)
            else:
                # Segundo elemento de la conexión
                elemento_destino = item[0]
                self.crear_flecha(self.elemento_origen, elemento_destino)
                
                # Resetear estado de conexión
                self.canvas.itemconfig(self.elemento_origen, outline="black", width=2)
                self.conexion_iniciada = False
                self.elemento_origen = None
                self.actualizar_texto_ayuda("Modo conexión: Haz clic en el primer elemento a conectar")
    
    def manejar_movimiento(self, event):
        if self.modo_conexion and self.conexion_iniciada:
            # Actualizar flecha temporal si estamos en modo conexión
            self.dibujar_flecha_temporal(event.x, event.y)
    
    def dibujar_flecha_temporal(self, x, y):
        # Eliminar flecha temporal anterior si existe
        if hasattr(self, 'flecha_temporal'):
            self.canvas.delete(self.flecha_temporal)
        
        if self.elemento_origen:
            # Obtener coordenadas del elemento origen
            x1, y1, x2, y2 = self.canvas.bbox(self.elemento_origen)
            centro_origen_x = (x1 + x2) / 2
            centro_origen_y = (y1 + y2) / 2
            
            # Dibujar flecha temporal
            self.flecha_temporal = self.canvas.create_line(
                centro_origen_x, centro_origen_y, x, y,
                arrow=tk.LAST, fill=self.color_flecha, width=2
            )
    
    def crear_flecha(self, origen, destino):
        # Obtener coordenadas de los elementos
        x1_origen, y1_origen, x2_origen, y2_origen = self.canvas.bbox(origen)
        x1_destino, y1_destino, x2_destino, y2_destino = self.canvas.bbox(destino)
        
        centro_origen_x = (x1_origen + x2_origen) / 2
        centro_origen_y = (y1_origen + y2_origen) / 2
        centro_destino_x = (x1_destino + x2_destino) / 2
        centro_destino_y = (y1_destino + y2_destino) / 2
        
        # Crear flecha permanente
        flecha = self.canvas.create_line(
            centro_origen_x, centro_origen_y,
            centro_destino_x, centro_destino_y,
            arrow=tk.LAST, fill=self.color_flecha, width=2
        )
        
        self.conexiones.append(flecha)
    
    def crear_figura(self, event):
        x, y = event.x, event.y
        tamaño = 60
        figura_id = None
        
        if self.figura_seleccionada.get() == "rectangulo":
            figura_id = self.canvas.create_rectangle(
                x-tamaño/2, y-tamaño/2, x+tamaño/2, y+tamaño/2,
                fill=self.color_relleno, outline="black", width=2
            )
        elif self.figura_seleccionada.get() == "ovalo":
            figura_id = self.canvas.create_oval(
                x-tamaño/2, y-tamaño/2, x+tamaño/2, y+tamaño/2,
                fill=self.color_relleno, outline="black", width=2
            )
        elif self.figura_seleccionada.get() == "rombo":
            figura_id = self.dibujar_rombo(x, y, tamaño)
        
        if figura_id:
            self.elementos.append(figura_id)
    
    def dibujar_rombo(self, x, y, tamaño):
        puntos = [
            x, y-tamaño/2,  # Punto superior
            x+tamaño/2, y,  # Punto derecho
            x, y+tamaño/2,   # Punto inferior
            x-tamaño/2, y   # Punto izquierdo
        ]
        return self.canvas.create_polygon(
            puntos,
            fill=self.color_relleno, outline="black", width=2
        )
    
    def limpiar_canvas(self):
        self.canvas.delete("all")
        self.elementos = []
        self.conexiones = []
        self.texto_ayuda = self.canvas.create_text(
            10, 10, 
            anchor="nw",
            text="Selecciona una figura y haz clic en el área para crearla",
            fill="gray50"
        )
        self.modo_conexion = False
        self.conexion_iniciada = False
        self.elemento_origen = None
        self.btn_conectar.config(text="Modo Conexión")

if __name__ == "__main__":
    root = tk.Tk()
    app = FigurasApp(root)
    root.mainloop()