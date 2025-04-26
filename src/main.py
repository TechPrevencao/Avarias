import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import requests
import sqlite3
import json

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Screen")
        self.root.state('zoomed')  # Full screen
        self.root.resizable(False, False)
        self.root.configure(bg='#000000')  # Full black background

        # Load and round the image
        image = Image.open("./src/login_image.png")
        image = image.resize((300, 300))
        rounded_image = self.round_image(image, 150)  # Radius = 150 for a 300x300 image
        photo = ImageTk.PhotoImage(rounded_image)

        self.image_label = tk.Label(self.root, image=photo, bg='#000000')
        self.image_label.image = photo
        self.image_label.pack(pady=50)

        self.main_frame = tk.Frame(self.root, bg='#1c1c1c', highlightthickness=0)  # Darker gray for contrast
        self.main_frame.pack(pady=20)

        self.username_label = tk.Label(self.main_frame, text="Usuário:", bg='#1c1c1c', fg='white', font=('Helvetica', 12))
        self.username_label.pack(pady=10)

        self.username_entry = tk.Entry(self.main_frame, width=30, bg='#333333', fg='white', highlightthickness=0, font=('Helvetica', 12))
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(self.main_frame, text="Senha:", bg='#1c1c1c', fg='white', font=('Helvetica', 12))
        self.password_label.pack(pady=10)

        self.password_entry = tk.Entry(self.main_frame, width=30, bg='#333333', fg='white', highlightthickness=0, font=('Helvetica', 12), show="*")
        self.password_entry.pack(pady=10)

        self.login_button = tk.Button(self.main_frame, text="Login", command=self.login, width=15, height=2, bg='#FFA500', fg='white', highlightthickness=0, font=('Helvetica', 12), activebackground='#FF8C00', activeforeground='white')
        self.login_button.pack(pady=20)

    def round_image(self, image, radius):
        """Rounds the corners of an image."""
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, image.size[0], image.size[1]), fill=255)
        rounded_image = Image.new("RGBA", image.size)
        rounded_image.paste(image, (0, 0), mask)
        return rounded_image

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if (username == "jobson" and password == "123") or (username == "italo" and password == "123"):
            self.root.destroy()
            new_root = tk.Tk()
            HomeScreen(new_root)
        else:
            messagebox.showerror("Credenciais Inválidas", "Por favor, tente novamente.")

class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Screen")
        self.root.state('zoomed')  # Full screen
        self.root.configure(bg='#000000')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(self.frame, text="Home")

        self.lateral_menu = tk.Frame(self.root, bg='#000000')
        self.lateral_menu.pack(side="left", fill="y")

        buttons = [
            ("Recuperação de Avarias", self.open_recuperacao_de_avarias),
            ("Furtos Recuperados", self.open_furtos_recuperados),
            ("Quebra do Mês", self.placeholder_command),
            ("Quebra por Degustação", self.placeholder_command),
            ("Avaria dos Ovos", self.placeholder_command),
            ("Avarias Padaria", self.placeholder_command),
            ("Avarias Rotisseria", self.placeholder_command),
            ("Avarias Salgados", self.placeholder_command),
            ("Avarias Açougue", self.placeholder_command),
            ("Mudança de Embalagens", self.placeholder_command),
            ("Controle de Maturattas", self.placeholder_command),
            ("Saída de Ossos", self.placeholder_command),
            ("Entrada de Carnes", self.placeholder_command),
            ("Entrada e Saída de Whisky's", self.placeholder_command),
            ("Requisições", self.placeholder_command),
            ("Prestadores de Serviços", self.placeholder_command),
            ("Acompanhamento de Laranjas", self.placeholder_command)
        ]

        # Add buttons dynamically
        for text, command in buttons:
            button = tk.Button(
                self.lateral_menu,
                text=text,
                bg='#FFA500',
                fg='white',
                highlightthickness=0,
                font=('Helvetica', 12),
                activebackground='#FF8C00',
                activeforeground='white',
                command=command  # Assign the specific command
            )
            button.pack(fill="x", pady=10)

    def open_recuperacao_de_avarias(self):
        """Open the Recuperação de Avarias window."""
        new_window = tk.Toplevel(self.root)
        RecuperacaoDeAvarias(new_window)

    def open_furtos_recuperados(self):
        """Open the Furtos Recuperados window."""
        new_window = tk.Toplevel(self.root)
        FurtosRecuperados(new_window)

    def placeholder_command(self, feature_name="Feature"):
        """Placeholder command for buttons."""
        messagebox.showinfo("Funcionalidade", f"Essa funcionalidade '{feature_name}' ainda não foi implementada.")


class RecuperacaoDeAvarias:
    def __init__(self, root):
        self.root = root
        self.root.title("Recuperação de Avarias")
        self.root.state('zoomed')  # Full screen
        self.root.configure(bg='#2b2b2b')

        # Input fields
        self.codigo_barras_label = tk.Label(self.root, text="Código Barras:", bg='#2b2b2b', fg='white')
        self.codigo_barras_label.pack(pady=10)
        self.codigo_barras_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.codigo_barras_entry.pack(pady=10)
        self.codigo_barras_entry.bind("<FocusOut>", self.on_codigo_barras_change)

        self.descricao_label = tk.Label(self.root, text="Descrição:", bg='#2b2b2b', fg='white')
        self.descricao_label.pack(pady=10)
        self.descricao_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.descricao_entry.pack(pady=10)

        self.quantidade_label = tk.Label(self.root, text="Quantidade:", bg='#2b2b2b', fg='white')
        self.quantidade_label.pack(pady=10)
        self.quantidade_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.quantidade_entry.pack(pady=10)

        self.codigo_interno_label = tk.Label(self.root, text="Código Interno:", bg='#2b2b2b', fg='white')
        self.codigo_interno_label.pack(pady=10)
        self.codigo_interno_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.codigo_interno_entry.pack(pady=10)

        self.departamento_label = tk.Label(self.root, text="Departamento:", bg='#2b2b2b', fg='white')
        self.departamento_label.pack(pady=10)
        self.departamento_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.departamento_entry.pack(pady=10)

        self.pvenda_label = tk.Label(self.root, text="Preço de Venda:", bg='#2b2b2b', fg='white')
        self.pvenda_label.pack(pady=10)
        self.pvenda_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.pvenda_entry.pack(pady=10)

        self.save_button = tk.Button(self.root, text="Salvar", command=self.salvar, bg='#4CAF50', fg='white', font=('Helvetica', 12))
        self.save_button.pack(pady=20)

    def on_codigo_barras_change(self, event):
        """Triggered when the Código Barras field loses focus."""
        codigo_barras = self.codigo_barras_entry.get().strip()
        if codigo_barras:
            self.consultar_dados(codigo_barras)

    def consultar_dados(self, codigo_barras):
        """Fetch data from the API based on the Código Barras."""
        url = "https://192.168.1.54:3001/dados?api_key=SAOROQUEsUvnQc0XVlRz9RvJcYNJ"
        payload = [{"Cod": codigo_barras, "Filial": "4"}]
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                if data:
                    item = data[0]
                    self.descricao_entry.delete(0, tk.END)
                    self.descricao_entry.insert(0, item.get("DESCRICAO", ""))

                    self.codigo_interno_entry.delete(0, tk.END)
                    self.codigo_interno_entry.insert(0, item.get("CODIGO", ""))

                    self.departamento_entry.delete(0, tk.END)
                    self.departamento_entry.insert(0, item.get("DEPARTAMENTO", ""))

                    self.pvenda_entry.delete(0, tk.END)
                    self.pvenda_entry.insert(0, item.get("PVENDA", ""))
                else:
                    messagebox.showerror("Erro", "Nenhum dado encontrado para o código de barras.")
            else:
                messagebox.showerror("Erro", f"Erro ao consultar dados. Status HTTP: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao servidor: {e}")

    def salvar(self):
        """Save the data entered in the form."""
        codigo_barras = self.codigo_barras_entry.get()
        descricao = self.descricao_entry.get()
        codigo_interno = self.codigo_interno_entry.get()
        departamento = self.departamento_entry.get()
        pvenda = self.pvenda_entry.get()

        connection = sqlite3.connect("dashboard.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO recuperacao_de_avarias (codigo_barras, descricao, codigo_interno, departamento, pvenda)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo_barras, descricao, codigo_interno, departamento, pvenda))
        connection.commit()
        connection.close()

        # Show a success message
        messagebox.showinfo("Sucesso", "Os dados foram salvos com sucesso!")

class FurtosRecuperados:
    def __init__(self, root):
        self.root = root
        self.root.title("Furtos Recuperados")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')

        # Input fields
        self.codigo_barras_label = tk.Label(self.root, text="Código Barras:", bg='#2b2b2b', fg='white')
        self.codigo_barras_label.pack(pady=10)
        self.codigo_barras_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.codigo_barras_entry.pack(pady=10)
        self.codigo_barras_entry.bind("<FocusOut>", self.on_codigo_barras_change)

        self.descricao_label = tk.Label(self.root, text="Descrição:", bg='#2b2b2b', fg='white')
        self.descricao_label.pack(pady=10)
        self.descricao_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.descricao_entry.pack(pady=10)

        self.quantidade_label = tk.Label(self.root, text="Quantidade:", bg='#2b2b2b', fg='white')
        self.quantidade_label.pack(pady=10)
        self.quantidade_entry = tk.Entry(self.root, width=30, bg='#f2f2f2', font=('Helvetica', 12))
        self.quantidade_entry.pack(pady=10)

        self.save_button = tk.Button(self.root, text="Salvar", command=self.salvar, bg='#4CAF50', fg='white', font=('Helvetica', 12))
        self.save_button.pack(pady=20)

    def on_codigo_barras_change(self, event):
        """Triggered when the Código Barras field loses focus."""
        codigo_barras = self.codigo_barras_entry.get().strip()
        if codigo_barras:
            self.consultar_dados(codigo_barras)

    def consultar_dados(self, codigo_barras):
        """Fetch data from the API based on the Código Barras."""
        url = "https://192.168.1.54:3001/dados?api_key=SAOROQUEsUvnQc0XVlRz9RvJcYNJ"
        payload = [{"Cod": codigo_barras, "Filial": "4"}]
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                if data:
                    item = data[0]
                    self.descricao_entry.delete(0, tk.END)
                    self.descricao_entry.insert(0, item.get("DESCRICAO", ""))

                    self.quantidade_entry.delete(0, tk.END)
                    self.quantidade_entry.insert(0, item.get("QUANTIDADE", ""))
                else:
                    messagebox.showerror("Erro", "Nenhum dado encontrado para o código de barras.")
            else:
                messagebox.showerror("Erro", f"Erro ao consultar dados. Status HTTP: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao servidor: {e}")

    def salvar(self):
        """Save the data entered in the form."""
        codigo_barras = self.codigo_barras_entry.get()
        descricao = self.descricao_entry.get()
        quantidade = self.quantidade_entry.get()

        # For now, print the data to the console
        print(f"Código Barras: {codigo_barras}")
        print(f"Descrição: {descricao}")
        print(f"Quantidade: {quantidade}")

        # Show a success message
        messagebox.showinfo("Sucesso", "Os dados foram salvos com sucesso!")

if __name__ == "__main__":
    def initialize_database():
        connection = sqlite3.connect("dashboard.db")  # Creates a file-based SQLite database
        cursor = connection.cursor()

        # Create a table for Recuperação de Avarias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recuperacao_de_avarias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT NOT NULL,
                descricao TEXT,
                codigo_interno TEXT,
                departamento TEXT,
                pvenda REAL
            )
        """)

        # Create a table for Furtos Recuperados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS furtos_recuperados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT NOT NULL,
                descricao TEXT,
                quantidade INTEGER
            )
        """)

        connection.commit()
        connection.close()
    root = tk.Tk()
    root.configure(bg='#000000')
    LoginScreen(root)
    root.mainloop()

    initialize_database()

