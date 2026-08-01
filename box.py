import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import cv2
import os
from camera_handler import CameraHandler

class PhotoBoothApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Booth - Nora und Tilman")
        self.root.geometry("1000x800")
        # self.root.attributes('-fullscreen', True)  # Später aktivieren
        
        self.camera = CameraHandler()
        
        # Farben
        self.colors = {
            'bg': '#fbf9e6',
            'primary': '#808e46',
            'secondary': '#c45f3f',
            'text': '#1a1e2e'
        }
        
        self.root.config(bg=self.colors['bg'])
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status
        self.current_photos = []
        self.is_capturing = False
        
        self.show_start_screen()
    
    def clear_frame(self):
        """Löscht alle Widgets im main_frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_start_screen(self):
        """Startbildschirm"""
        self.clear_frame()
        
        # Titel
        title = tk.Label(
            self.main_frame,
            text="Nora und Tilman",
            font=("Helvetica", 48, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title.pack(pady=50)
        
        # Motto
        motto = tk.Label(
            self.main_frame,
            text="nothing fancy, just love",
            font=("Helvetica", 24),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        motto.pack(pady=10)
        
        # RUNDER START BUTTON
        button_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        button_frame.pack(pady=100)
        
        start_btn = tk.Button(
            button_frame,
            text="Start",
            font=("Helvetica", 28, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['bg'],
            padx=40,
            pady=20,
            relief=tk.RAISED,
            bd=0,
            command=self.start_photo_series,
            cursor="hand2"
        )
        start_btn.pack()
        
        # Hover-Effekt
        def on_enter(e):
            start_btn.config(bg=self.colors['secondary'])
        def on_leave(e):
            start_btn.config(bg=self.colors['primary'])
        start_btn.bind("<Enter>", on_enter)
        start_btn.bind("<Leave>", on_leave)
    
    def start_photo_series(self):
        """Startet die 4er Fotoserie"""
        self.current_photos = []
        self.photo_series([10, 3, 3, 3])
    
    def photo_series(self, countdowns):
        """Steuert die Fotoserie mit verschieden langen Countdowns"""
        if not countdowns:
            # Alle Fotos fertig → Confirmation Screen
            self.show_confirmation_screen()
            return
        
        countdown = countdowns[0]
        remaining = countdowns[1:]
        
        # Countdown anzeigen
        threading.Thread(target=self.countdown_and_capture, args=(countdown, remaining), daemon=True).start()
    
    def countdown_and_capture(self, countdown, remaining):
        """Zeigt Countdown an und macht Foto"""
        self.clear_frame()
        self.is_capturing = True
        
        countdown_label = tk.Label(
            self.main_frame,
            text=str(countdown),
            font=("Helvetica", 120, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['primary']
        )
        countdown_label.pack(expand=True)
        
        # Countdown herunterzählen
        for i in range(countdown, 0, -1):
            countdown_label.config(
                text=str(i),
                fg=self.colors['secondary'] if i <= 3 else self.colors['primary']
            )
            self.root.update()
            self.root.after(1000)
        
        # FOTO AUFNEHMEN
        photo_path = self.camera.capture_image()
        
        if photo_path:
            self.current_photos.append(photo_path)
            # Foto anzeigen
            self.show_photo(photo_path, remaining)
        else:
            print("❌ Foto fehlgeschlagen")
            self.show_start_screen()
    
    def show_photo(self, photo_path, remaining):
        """Zeigt das aufgenommene Foto an"""
        self.clear_frame()
        
        try:
            img = Image.open(photo_path)
            img.thumbnail((600, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            img_label = tk.Label(self.main_frame, image=photo, bg=self.colors['bg'])
            img_label.image = photo  # Keep reference
            img_label.pack(pady=50)
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen: {e}")
        
        # Weiter nach 2 Sekunden
        self.root.after(2000, lambda: self.photo_series(remaining))
    
    def show_confirmation_screen(self):
        """Zeigt die 4 Fotos in 2x2 Grid"""
        self.clear_frame()
        
        # Titel
        title = tk.Label(
            self.main_frame,
            text="Deine Fotos",
            font=("Helvetica", 32, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title.pack(pady=20)
        
        # Grid Frame (2x2)
        grid_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        grid_frame.pack(pady=20)
        
        for i, photo_path in enumerate(self.current_photos):
            try:
                img = Image.open(photo_path)
                img.thumbnail((240, 240), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                img_label = tk.Label(grid_frame, image=photo, bg=self.colors['bg'])
                img_label.image = photo
                row, col = divmod(i, 2)
                img_label.grid(row=row, column=col, padx=10, pady=10)
            except Exception as e:
                print(f"❌ Fehler: {e}")
        
        # Buttons
        btn_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=30)
        
        # Nochmal Button
        nochmal_btn = tk.Button(
            btn_frame,
            text="Nochmal",
            font=("Helvetica", 16, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['bg'],
            padx=30,
            pady=15,
            relief=tk.FLAT,
            command=self.show_start_screen,
            cursor="hand2"
        )
        nochmal_btn.grid(row=0, column=0, padx=20)
        
        # Fertig Button
        fertig_btn = tk.Button(
            btn_frame,
            text="Fertig",
            font=("Helvetica", 16, "bold"),
            bg=self.colors['secondary'],
            fg=self.colors['bg'],
            padx=30,
            pady=15,
            relief=tk.FLAT,
            command=self.show_start_screen,
            cursor="hand2"
        )
        fertig_btn.grid(row=0, column=1, padx=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoBoothApp(root)
    root.mainloop()
