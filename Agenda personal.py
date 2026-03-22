import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
from tkcalendar import DateEntry  # pip install tkcalendar


class AgendaPersonal:
    def __init__(self, root):
        """
        Inicializa la aplicación de Agenda Personal
        """
        self.root = root
        self.root.title("📅 Agenda Personal")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Lista para almacenar los eventos (fecha, hora, descripción)
        self.eventos = []
        self.cargar_eventos()

        # Configurar estilo
        self.configurar_estilos()

        # Crear la interfaz
        self.crear_interfaz()

        # Cargar eventos en la tabla
        self.actualizar_lista_eventos()

    def configurar_estilos(self):
        """Configura los estilos de los widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

    def crear_interfaz(self):
        """Crea toda la interfaz gráfica usando Frames"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar pesos para que se expanda
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 1. Título
        titulo = ttk.Label(main_frame, text="📅 Mi Agenda Personal",
                           style='Title.TLabel')
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 2. Frame para entrada de datos (izquierda)
        frame_entrada = ttk.LabelFrame(main_frame, text="➕ Nuevo Evento",
                                       padding="10")
        frame_entrada.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N),
                           padx=(0, 10), pady=10)

        # Campos de entrada
        ttk.Label(frame_entrada, text="Fecha:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_fecha = DateEntry(frame_entrada, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.entry_fecha.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_entrada, text="Hora (HH:MM):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_hora = ttk.Entry(frame_entrada, width=15)
        self.entry_hora.grid(row=1, column=1, padx=5, pady=5)
        self.entry_hora.insert(0, "09:00")  # Hora por defecto

        ttk.Label(frame_entrada, text="Descripción:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=5)
        self.entry_desc = tk.Text(frame_entrada, width=25, height=4)
        self.entry_desc.grid(row=2, column=1, padx=5, pady=5)

        # Botón Agregar
        btn_agregar = ttk.Button(frame_entrada, text="➕ Agregar Evento",
                                 command=self.agregar_evento)
        btn_agregar.grid(row=3, column=0, columnspan=2, pady=15)

        # 3. Frame para lista de eventos (derecha)
        frame_lista = ttk.LabelFrame(main_frame, text="📋 Eventos Programados",
                                     padding="10")
        frame_lista.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # TreeView para mostrar eventos
        columnas = ("Fecha", "Hora", "Descripción")
        self.tree = ttk.Treeview(frame_lista, columns=columnas, show='headings', height=15)

        # Configurar encabezados
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Descripción", text="Descripción")

        # Configurar columnas
        self.tree.column("Fecha", width=100)
        self.tree.column("Hora", width=80)
        self.tree.column("Descripción", width=300)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Vincular selección para eliminar
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # 4. Frame para botones de acción (abajo)
        frame_botones = ttk.Frame(main_frame)
        frame_botones.grid(row=2, column=0, columnspan=2, pady=20)

        self.btn_eliminar = ttk.Button(frame_botones, text="🗑️ Eliminar Seleccionado",
                                       command=self.eliminar_evento, state='disabled')
        self.btn_eliminar.pack(side=tk.LEFT, padx=10)

        ttk.Button(frame_botones, text="🔄 Actualizar Lista",
                   command=self.actualizar_lista_eventos).pack(side=tk.LEFT, padx=10)

        ttk.Button(frame_botones, text="❌ Salir",
                   command=self.salir).pack(side=tk.RIGHT, padx=10)

    def agregar_evento(self):
        """Agrega un nuevo evento a la lista"""
        fecha = self.entry_fecha.get_date().strftime("%d/%m/%Y")
        hora = self.entry_hora.get().strip()
        descripcion = self.entry_desc.get("1.0", tk.END).strip()

        # Validaciones
        if not hora or not descripcion:
            messagebox.showerror("Error", "Por favor completa hora y descripción")
            return

        if len(hora) != 5 or hora[2] != ":":
            messagebox.showerror("Error", "Formato de hora inválido (HH:MM)")
            return

        # Crear evento
        evento = {
            'fecha': fecha,
            'hora': hora,
            'descripcion': descripcion[:100]  # Limitar longitud
        }

        self.eventos.append(evento)
        self.guardar_eventos()
        self.actualizar_lista_eventos()

        # Limpiar campos
        self.entry_hora.delete(0, tk.END)
        self.entry_desc.delete("1.0", tk.END)
        self.entry_hora.insert(0, "09:00")

        messagebox.showinfo("Éxito", "✅ Evento agregado correctamente")

    def eliminar_evento(self):
        """Elimina el evento seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un evento para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este evento?"):
            item = self.tree.item(seleccion)
            indice = self.tree.index(seleccion[0])
            del self.eventos[indice]
            self.guardar_eventos()
            self.actualizar_lista_eventos()
            self.btn_eliminar.config(state='disabled')
            messagebox.showinfo("Éxito", "✅ Evento eliminado correctamente")

    def on_select(self, event):
        """Habilita botón eliminar cuando se selecciona un evento"""
        seleccion = self.tree.selection()
        self.btn_eliminar.config(state='normal' if seleccion else 'disabled')

    def actualizar_lista_eventos(self):
        """Actualiza la tabla con todos los eventos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ordenar eventos por fecha y hora
        eventos_ordenados = sorted(self.eventos, key=lambda x: (x['fecha'], x['hora']))

        # Agregar eventos a la tabla
        for evento in eventos_ordenados:
            self.tree.insert('', tk.END, values=(
                evento['fecha'],
                evento['hora'],
                evento['descripcion']
            ))

    def guardar_eventos(self):
        """Guarda los eventos en un archivo JSON"""
        try:
            with open('eventos.json', 'w', encoding='utf-8') as f:
                json.dump(self.eventos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar: {e}")

    def cargar_eventos(self):
        """Carga los eventos desde archivo JSON"""
        try:
            with open('eventos.json', 'r', encoding='utf-8') as f:
                self.eventos = json.load(f)
        except FileNotFoundError:
            self.eventos = []
        except Exception as e:
            print(f"Error al cargar: {e}")
            self.eventos = []

    def salir(self):
        """Cierra la aplicación guardando los cambios"""
        self.guardar_eventos()
        self.root.quit()


def main():
    """Función principal para ejecutar la aplicación"""
    root = tk.Tk()
    app = AgendaPersonal(root)
    root.mainloop()


if __name__ == "__main__":
    main()