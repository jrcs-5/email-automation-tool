import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
from database import Database
from logic import start_scheduler_in_thread

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recordatorios Automáticos")
        self.db = Database()

        # Frame de la barra lateral
        self.sidebar_frame = tk.Frame(self.root, width=250, height=500, bg="#f0f0f0")
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Frame de la lista de recordatorios
        self.text_list_frame = tk.Frame(self.root, width=450, height=500)
        self.text_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar para la lista de textos
        self.scrollbar = tk.Scrollbar(self.text_list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Lista de textos (Treeview)
        self.text_treeview = ttk.Treeview(self.text_list_frame, columns=("Asunto", "Fecha", "Pendiente", "Fallido", "Enviado"), show="headings", yscrollcommand=self.scrollbar.set)
        self.text_treeview.pack(fill=tk.BOTH, expand=True)
        
        self.text_treeview.heading("Asunto", text="Asunto")
        self.text_treeview.heading("Fecha", text="Fecha")
        self.text_treeview.heading("Pendiente", text="Pendiente")
        self.text_treeview.heading("Fallido", text="Fallido")
        self.text_treeview.heading("Enviado", text="Enviado")
        
        self.text_treeview.column("Asunto", width=150)
        self.text_treeview.column("Fecha", width=130)
        self.text_treeview.column("Pendiente", width=70)
        self.text_treeview.column("Fallido", width=70)
        self.text_treeview.column("Enviado", width=70)


        # Cargar textos al inicio
        self.load_texts()
        
        self.schedule_table_reload()
        
        # Botón para agregar recordatorio
        self.add_reminder_button = tk.Button(self.root, text="Agregar Recordatorio", command=self.open_reminder_form)
        self.add_reminder_button.pack(side=tk.BOTTOM, pady=10)

        # Iniciar la ejecución paralela del proceso de recordatorios
        start_scheduler_in_thread()
        
    def load_texts(self):
        """Carga los textos desde la base de datos y los muestra en la lista."""
        texts = self.db.get_texts()
        # Limpiar los elementos previos
        for item in self.text_treeview.get_children():
            self.text_treeview.delete(item)
        
        for text in texts:
            self.text_treeview.insert("", tk.END, values=(text[0], text[2], text[3], text[4], text[5]))
            
            
    def open_reminder_form(self):
        """Abre un formulario para agregar un nuevo recordatorio."""
        self.form_window = tk.Toplevel(self.root)
        self.form_window.title("Nuevo Recordatorio")

        # Campo de asunto
        self.asunto_label = tk.Label(self.form_window, text="Asunto")
        self.asunto_label.pack()
        self.asunto_entry = tk.Entry(self.form_window, width=50)
        self.asunto_entry.pack()
        
        # Campo de mensaje
        self.mensaje_label = tk.Label(self.form_window, text="Mensaje")
        self.mensaje_label.pack()
        self.mensaje_text = tk.Text(self.form_window, height=10, width=50)
        self.mensaje_text.pack()
        
        # Campo de fecha con DateEntry
        self.fecha_label = tk.Label(self.form_window, text="Fecha (yyyy-mm-dd hh:mm:ss)")
        self.fecha_label.pack()
        
        # Crear el DateEntry para la fecha
        self.fecha_dateentry = DateEntry(self.form_window, width=12, date_pattern="yyyy-mm-dd", state="normal")
        self.fecha_dateentry.pack()

        # Campo de hora (con minutos y segundos por defecto a 00)
        self.hora_label = tk.Label(self.form_window, text="Hora (hh:mm)")
        self.hora_label.pack()
        self.hora_entry = tk.Entry(self.form_window, width=12)
        self.hora_entry.insert(tk.END, "00:00")  # Hora predeterminada
        self.hora_entry.pack()

        self.clients_frame = tk.Frame(self.form_window)
        self.clients_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.select_all_button = tk.Button(self.clients_frame, text="Seleccionar Todos", command=self.select_all_clients)
        self.select_all_button.pack()
        
        self.clientes = self.db.get_clients()
        self.cliente_checkbuttons = []
        for client in self.clientes:
            var = tk.IntVar()
            checkbutton = tk.Checkbutton(self.clients_frame, text=f"{client[1]} {client[2]}", variable=var)
            checkbutton.pack(anchor="w")
            self.cliente_checkbuttons.append((var, client))
            
            
        self.save_button = tk.Button(self.form_window, text="Guardar", command=self.save_reminder)
        self.save_button.pack(pady=10)

    def select_all_clients(self):
        """Selecciona todos los clientes."""
        all_selected = all(var.get() == 1 for var, _ in self.cliente_checkbuttons)

        for var, _ in self.cliente_checkbuttons:
            var.set(0) if all_selected else var.set(1)
        
        
    def save_reminder(self):
        """Guarda el recordatorio y los clientes seleccionados en la bd"""
        subject = self.asunto_entry.get()
        message = self.mensaje_text.get("1.0", tk.END).strip()
        fecha = self.fecha_dateentry.get()
        hora = self.hora_entry.get()
        fecha_hora = f"{fecha} {hora}:00"

        try:
            reminder_date = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("Fecha inválida")
            return
        
        
        # Filtrar clientes seleccionados
        selected_clients = [client for var, client in self.cliente_checkbuttons if var.get() == 1]

        # Agregar el texto
        id_texto = self.db.add_text(subject, message, reminder_date)

        # Agregar recordatorio
        self.db.add_reminder(selected_clients, id_texto, reminder_date)

        # Cerrar formulario
        self.form_window.destroy()

        # Actualizar lista de textos
        self.load_texts()
        
    def schedule_table_reload(self):
        self.load_texts()
        self.root.after(10000, self.schedule_table_reload)
        
        
if __name__ == "__main__":
    # Iniciar la ventana principal
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()