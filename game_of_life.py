import tkinter as tk
from tkinter import messagebox
import json

class SettingsManager:
    """Zarządza ustawieniami aplikacji, w tym ładowaniem i zapisywaniem do pliku JSON."""
    
    def __init__(self):
        self.settings_file = "settings.json"
        self.load_settings()
    
    def load_settings(self):
        """Wczytaj ustawienia z pliku JSON lub ustaw wartości domyślne, jeśli ich nie znaleziono."""
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                self.grid_width = data.get('grid_width', 30)
                self.grid_height = data.get('grid_height', 30)
                self.cell_size = data.get('cell_size', 20)
                self.update_interval = data.get('update_interval', 100)
        except (FileNotFoundError, json.JSONDecodeError):
            self.set_defaults()
    
    def set_defaults(self):
        """Ustaw wartości ustawień domyślnych."""
        self.grid_width = 30
        self.grid_height = 30
        self.cell_size = 20
        self.update_interval = 100
    
    def save_settings(self, grid_width, grid_height, cell_size, update_interval):
        """Zapisuje bieżące ustawienia do pliku JSON."""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.update_interval = update_interval
        data = {
            'grid_width': grid_width,
            'grid_height': grid_height,
            'cell_size': cell_size,
            'update_interval': update_interval
        }
        with open(self.settings_file, 'w') as f:
            json.dump(data, f)

class GameOfLife:
    """Implementuje logikę symulacji gry w życie Conwaya."""
    
    def __init__(self, width, height):
        """Inicjuje siatkę o określonych wymiarach."""
        self.width = width
        self.height = height
        self.grid = [[False for _ in range(width)] for _ in range(height)]
    
    def next_generation(self):
        """Oblicz następną generację na podstawie reguł Conwaya."""
        new_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                if self.grid[y][x]:
                    new_grid[y][x] = 2 <= neighbors <= 3
                else:
                    new_grid[y][x] = neighbors == 3
        self.grid = new_grid
    
    def count_neighbors(self, x, y):
        """Policz żywych sąsiadów wokół komórki (x, y)."""
        count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    count += self.grid[ny][nx]
        return count
    
    def toggle_cell(self, x, y):
        """Przełącza stan komórki w punkcie (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = not self.grid[y][x]
    
    def clear_grid(self):
        """Zresetuj wszystkie komórki do stanu śmierci."""
        self.grid = [[False for _ in range(self.width)] for _ in range(self.height)]

class App(tk.Tk):
    """Główna klasa aplikacji dla GUI gry w życie."""
    
    def __init__(self):
        super().__init__()
        self.title("Gra w życie Conwaya")
        self.geometry("800x600")
        self.settings = SettingsManager()
        self.show_start_screen()
    
    def show_start_screen(self):
        """Wyświetlenie ekranu startowego z przyciskami nawigacyjnymi."""
        if hasattr(self, 'current_frame'):
            self.current_frame.destroy()
        self.current_frame = StartFrame(self)
        self.current_frame.pack(expand=True)
    
    def show_settings_screen(self):
        """Wyświetlenie ekranu regulacji ustawień."""
        self.current_frame.destroy()
        self.current_frame = SettingsFrame(self)
        self.current_frame.pack(expand=True)
    
    def show_game_screen(self):
        """Wyświetlenie ekranu symulacji gry."""
        self.current_frame.destroy()
        self.current_frame = GameFrame(self)
        self.current_frame.pack(expand=True)

class StartFrame(tk.Frame):
    """Ramka ekranu startowego z przyciskami nawigacyjnymi."""
    
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        tk.Button(self, text="Rozpocznij grę", command=master.show_game_screen).pack(pady=10)
        tk.Button(self, text="Ustawienia", command=master.show_settings_screen).pack(pady=10)
        tk.Button(self, text="Wyjdź", command=master.quit).pack(pady=10)

class SettingsFrame(tk.Frame):
    """Ramka regulacji ustawień z polami wejściowymi."""
    
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.entries = {}
        labels = [
            ('Szerokość siatki', master.settings.grid_width),
            ('Wysokość siatki', master.settings.grid_height),
            ('Rozmiar komórki', master.settings.cell_size),
            ('Częstotliwość aktualizacji (ms)', master.settings.update_interval)
        ]
        for i, (text, default) in enumerate(labels):
            tk.Label(self, text=text).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(self)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[text] = entry
        tk.Button(self, text="Zapisz", command=self.save).grid(row=len(labels), column=0, pady=10)
        tk.Button(self, text="Powrót", command=self.master.show_start_screen).grid(row=len(labels), column=1, pady=10)
    
    def save(self):
        """Zapisywanie ustawień z pól wejściowych."""
        try:
            width = int(self.entries['Szerokość siatki'].get())
            height = int(self.entries['Wysokość siatki'].get())
            cell_size = int(self.entries['Rozmiar komórki'].get())
            interval = int(self.entries['Częstotliwość aktualizacji (ms)'].get())
            if width < 1 or height < 1 or cell_size < 1 or interval < 1:
                raise ValueError("Wartości muszą być dodatnimi liczbami całkowitymi.")
            self.master.settings.save_settings(width, height, cell_size, interval)
            self.master.show_start_screen()
        except ValueError as e:
            messagebox.showerror("Nieprawidłowe dane wejściowe", str(e))

class GameFrame(tk.Frame):
    """Ramka symulacji gry z interaktywną siatką i elementami sterującymi."""
    
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.game = GameOfLife(master.settings.grid_width, master.settings.grid_height)
        self.running = False
        self.after_id = None
        self.setup_ui()
    
    def setup_ui(self):
        """Inicjalizacja komponentów interfejsu użytkownika."""
        self.canvas = tk.Canvas(self, width=self.master.settings.grid_width * self.master.settings.cell_size, height=self.master.settings.grid_height * self.master.settings.cell_size, bg='white')
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.controls = tk.Frame(self)
        self.controls.pack(pady=10)
        self.start_btn = tk.Button(self.controls, text="Start", command=self.toggle_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls, text="Wyczyść", command=self.clear_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls, text="Powrót", command=self.master.show_start_screen).pack(side=tk.LEFT, padx=5)
        self.draw_grid()
    
    def on_canvas_click(self, event):
        """Obsługa zdarzeń kliknięcia kanwy w celu przełączania komórek."""
        x = event.x // self.master.settings.cell_size
        y = event.y // self.master.settings.cell_size
        self.game.toggle_cell(x, y)
        self.draw_grid()
    
    def draw_grid(self):
        """Rysuje bieżący stan siatki na płótnie."""
        self.canvas.delete("all")
        cell_size = self.master.settings.cell_size
        for y in range(self.game.height):
            for x in range(self.game.width):
                color = 'black' if self.game.grid[y][x] else 'white'
                x0 = x * cell_size
                y0 = y * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='gray')
    
    def toggle_simulation(self):
        """Przełączanie stanu działania symulacji."""
        self.running = not self.running
        self.start_btn.config(text="Stop" if self.running else "Start")
        if self.running:
            self.run_simulation()
    
    def run_simulation(self):
        """Uruchom etap symulacji."""
        if self.running:
            self.game.next_generation()
            self.draw_grid()
            self.after_id = self.after(self.master.settings.update_interval, self.run_simulation)
    
    def clear_grid(self):
        """Wyczyść siatkę i zatrzymaj symulację."""
        self.running = False
        self.start_btn.config(text="Start")
        if self.after_id:
            self.after_cancel(self.after_id)
        self.game.clear_grid()
        self.draw_grid()

if __name__ == "__main__":
    app = App()
    app.mainloop()