import sys
import cv2
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import (
    QFont, QColor, QPixmap, QPainter, QPainterPath, QBrush, 
    QPen, QImage
)

from camera_handler import CameraHandler

# ============================================================================
# FARBEN
# ============================================================================
COLORS = {
    "bg_blau": "#6777b6",
    "bg_lila": "#7b68a6",
    "gold": "#e8d481",
    "gold_dark": "#c9af4d",
    "coral": "#d97a5e",
    "rosa": "#e8a4c4",
    "rosa_light": "#f0d5e8",
    "navy": "#1a1e2e",
    "creme": "#f9f9e6",}
# ============================================================================
# CUSTOM WIDGETS
# ============================================================================
class OrganicWaveWidget(QWidget):
    """Organische wellige Welle oben/unten"""
    
    def __init__(self, position="top", color=COLORS["gold"], parent=None):
        super().__init__(parent)
        self.position = position
        self.color = color
        self.animation_offset = 0
        self.setStyleSheet("background: transparent;")
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(80)
    
    def update_animation(self):
        self.animation_offset = (self.animation_offset + 1) % 100
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Mehrere wellige Linien für Textur
        for line_idx in range(3):
            path = QPainterPath()
            offset_shift = line_idx * 15
            
            pen = QColor(self.color)
            pen_width = QPen(pen)
            pen_width.setWidth(2 if line_idx == 0 else 1)
            painter.setPen(pen_width)
            
            if self.position == "top":
                start_y = 20 + line_idx * 12
                path.moveTo(0, start_y)
                
                for x in range(0, w + 50, 50):
                    wave_offset = (self.animation_offset + offset_shift + x / 10) % 100
                    y = start_y + 8 * ((wave_offset / 50) - 1) ** 2
                    path.lineTo(x, y)
            else:
                start_y = h - 20 - line_idx * 12
                path.moveTo(0, start_y)
                
                for x in range(0, w + 50, 50):
                    wave_offset = (self.animation_offset + offset_shift + x / 10) % 100
                    y = start_y - 8 * ((wave_offset / 50) - 1) ** 2
                    path.lineTo(x, y)
            
            painter.drawPath(path)
class OrganicFrameWidget(QWidget):
    """Organischer welliger Rahmen um Fotos"""

    def __init__(self, photo_path=None, parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.animation_offset = 0
        self.setStyleSheet("background: transparent;")
        
        if photo_path:
            self.pixmap = QPixmap(photo_path)
        else:
            self.pixmap = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)
    
    def update_animation(self):
        self.animation_offset = (self.animation_offset + 0.3) % 100
        self.update()
    
    def set_photo(self, photo_path):
        """Foto aktualisieren"""
        if photo_path:
            self.pixmap = QPixmap(photo_path)
            self.update()
    
    def paintEvent(self, event):
        if not self.pixmap:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Skaliertes Foto mit Padding
        padding = 30
        photo_width = w - 2 * padding
        photo_height = h - 2 * padding
        
        scaled_pixmap = self.pixmap.scaledToWidth(int(photo_width), Qt.SmoothTransformation)
        
        # Foto zentriert
        photo_x = padding + (photo_width - scaled_pixmap.width()) / 2
        photo_y = padding + (photo_height - scaled_pixmap.height()) / 2
        painter.drawPixmap(int(photo_x), int(photo_y), scaled_pixmap)
        
        # Organischer welliger Rahmen
        frame_path = QPainterPath()
        
        # Top-Linie
        frame_path.moveTo(padding - 10, padding)
        for i in range(int((w - 2 * padding + 20) / 20) + 1):
            offset = (self.animation_offset + i * 8) % 100
            y_offset = padding + 6 * ((offset / 50) - 1) ** 2
            frame_path.lineTo(padding - 10 + i * 20, y_offset)
        
        # Right-Linie
        frame_path.lineTo(w - padding, padding)
        for i in range(int((h - 2 * padding) / 20) + 1):
            offset = (self.animation_offset + i * 8 + 25) % 100
            x_offset = w - padding - 6 * ((offset / 50) - 1) ** 2
            frame_path.lineTo(x_offset, padding + i * 20)
        
        # Bottom-Linie
        frame_path.lineTo(w - padding, h - padding)
        for i in range(int((w - 2 * padding + 20) / 20) + 1, -1, -1):
            offset = (self.animation_offset + i * 8 + 50) % 100
            y_offset = h - padding - 6 * ((offset / 50) - 1) ** 2
            frame_path.lineTo(padding - 10 + i * 20, y_offset)
        
        # Left-Linie
        frame_path.lineTo(padding - 10, h - padding)
        for i in range(int((h - 2 * padding) / 20) + 1, -1, -1):
            offset = (self.animation_offset + i * 8 + 75) % 100
            x_offset = padding + 6 * ((offset / 50) - 1) ** 2
            frame_path.lineTo(x_offset, h - padding - i * 20)
        
        frame_path.closeSubpath()
        
        pen = QPen(QColor(COLORS["rosa_light"]))
        pen.setWidth(3)
        painter.strokePath(frame_path, pen)
class FloatingDecoration(QWidget):
    """Schwebende, pulsierende Punkte"""
    
    def __init__(self, color=COLORS["rosa"], position=(100, 100), size=25, parent=None):
        super().__init__(parent)
        self.color = color
        self.base_pos = position
        self.size = size
        self.pulse_offset = 0
        self.setStyleSheet("background: transparent;")
        self.setGeometry(QRect(position[0] - size * 2, position[1] - size * 2, 
                               size * 4, size * 4))
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pulse)
        self.timer.start(30)
    
    def update_pulse(self):
        self.pulse_offset = (self.pulse_offset + 1) % 100
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Puls-Effekt
        pulse = 0.7 + 0.3 * abs((self.pulse_offset / 50) - 1)
        current_size = self.size * pulse
        alpha = int(100 + 100 * ((self.pulse_offset / 50) - 1) ** 2)
        
        color = QColor(self.color)
        color.setAlpha(min(255, alpha))
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        
        center = self.size * 2
        painter.drawEllipse(int(center - current_size / 2), 
                           int(center - current_size / 2),
                           int(current_size), int(current_size))
 # ============================================================================
# SCREENS
# ============================================================================
class StartScreen(QWidget):
    """Start-Screen mit organischen Wellen & Motto"""
    
    start_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet(f"background-color: {COLORS['bg_blau']};")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top Wave
        top_wave = OrganicWaveWidget(position="top", color=COLORS["gold"])
        main_layout.addWidget(top_wave)
        
        # Center Content
        center_layout = QVBoxLayout()
        center_layout.setSpacing(30)
        center_layout.setContentsMargins(60, 60, 60, 60)
        
        # Title
        title = QLabel("Nora & Tilman")
        title_font = QFont("Inria Serif", 72, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['gold']}; background: transparent;")
        center_layout.addWidget(title)
        
        center_layout.addSpacing(20)
        
        # Motto - GRÖSSER und besser lesbar
        motto = QLabel("nothing fancy,\njust love")
        motto_font = QFont("Courier", 42, QFont.Light)
        motto.setFont(motto_font)
        motto.setAlignment(Qt.AlignCenter)
        motto.setStyleSheet(f"color: {COLORS['rosa_light']}; background: transparent; line-height: 60px;")
        motto.setMinimumHeight(150)
        center_layout.addWidget(motto)
        
        center_layout.addStretch(2)
        
        # Start Button
        start_btn = QPushButton("START")
        start_btn.setFixedSize(200, 200)
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['coral']};
                border: 4px solid {COLORS['gold']};
                border-radius: 100px;
                color: {COLORS['creme']};
                font-size: 32px;
                font-weight: bold;
                font-family: Inria Serif;
            }}
            QPushButton:hover {{
                background-color: {COLORS['rosa']};
                border: 4px solid {COLORS['rosa_light']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['gold_dark']};
            }}
        """)
        start_btn.clicked.connect(self.start_clicked.emit)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(start_btn)
        btn_layout.addStretch()
        center_layout.addLayout(btn_layout)
        
        center_layout.addStretch()
        
        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        main_layout.addWidget(center_widget, 1)
        
        # Bottom Wave
        bottom_wave = OrganicWaveWidget(position="bottom", color=COLORS["rosa"])
        main_layout.addWidget(bottom_wave)
        
        # Floating Decorations - größer und prägnanter
        decorations = [
            (COLORS["gold"], (80, 250), 20),
            (COLORS["rosa"], (100, 600), 25),
            (COLORS["gold_dark"], (1100, 200), 18),
            (COLORS["rosa_light"], (1120, 650), 22),
        ]
        
        for color, pos, size in decorations:
            FloatingDecoration(color, pos, size, self)
        
        self.setLayout(main_layout)
class PhotoSeriesScreen(QWidget):
    """Photo Series: Countdown + Webcam/Fotos Preview"""
    
    series_complete = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera = CameraHandler()
        self.photos = []
        self.current_photo_index = 0
        self.countdown = 0
        self.webcam = None
        self.webcam_active = False
        self.last_frame = None
        self.timer = QTimer()  # ← HINZUGEFÜGT
        self.timer.timeout.connect(self.update_countdown)  # ← HINZUGEFÜGT
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet(f"background-color: {COLORS['bg_lila']};")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top Wave
        top_wave = OrganicWaveWidget(position="top", color=COLORS["gold"])
        layout.addWidget(top_wave)
        
        # Center Content
        center_layout = QVBoxLayout()
        center_layout.setSpacing(30)
        center_layout.setContentsMargins(50, 40, 50, 40)
        
        # Preview Label (für Webcam oder Fotos)
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(700, 550)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(f"""
            border: 12px solid {COLORS['gold']};
            border-radius: 8px;
            background-color: {COLORS['navy']};
        """)
        
        preview_wrapper = QHBoxLayout()
        preview_wrapper.addStretch()
        preview_wrapper.addWidget(self.preview_label)
        preview_wrapper.addStretch()
        center_layout.addLayout(preview_wrapper)
        
        # Countdown Label
        self.timer_label = QLabel("Bereit?")
        timer_font = QFont("Inria Serif", 48, QFont.Bold)
        self.timer_label.setFont(timer_font)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet(f"color: {COLORS['bg_blau']}; background: transparent;")
        center_layout.addWidget(self.timer_label)
        
        center_layout.addStretch()
        
        layout.addLayout(center_layout, 1)
        
        # Bottom Wave
        bottom_wave = OrganicWaveWidget(position="bottom", color=COLORS["rosa"])
        layout.addWidget(bottom_wave)
        
        self.setLayout(layout)
    
    def start_series(self):
        """Start photo series"""
        self.current_photo_index = 0
        self.photos = []
        self.webcam = cv2.VideoCapture(0)
        self.webcam_active = True
        self.next_photo()
    
    def next_photo(self):
        """Start countdown for next photo"""
        if self.current_photo_index >= 3:
            # Series complete
            self.webcam_active = False
            if self.webcam:
                self.webcam.release()
            self.series_complete.emit(self.photos)
            return
        
        # First photo: 6 seconds (mit Webcam), others: 2 seconds (mit vorherigem Foto)
        self.countdown = 6 if self.current_photo_index == 0 else 2
        self.timer.start(1000)  # ← GEÄNDERT: Timer starten
        self.update_countdown()
    
    def update_countdown(self):
        """Update countdown and preview"""
        self.timer_label.setText(str(self.countdown))
        
        # Zeige Webcam beim ersten Countdown, sonst das letzte Foto
        if self.current_photo_index == 0 and self.webcam_active:
            ret, frame = self.webcam.read()
            if ret:
                self.last_frame = frame
                # Mirror frame
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                self.preview_label.setPixmap(pixmap.scaledToWidth(700, Qt.SmoothTransformation))
        elif self.current_photo_index > 0 and len(self.photos) > 0:
            # Zeige das letzte Foto
            pixmap = QPixmap(self.photos[-1])
            self.preview_label.setPixmap(pixmap.scaledToWidth(700, Qt.SmoothTransformation))
        
        if self.countdown > 0:
            self.countdown -= 1
        else:
            self.timer.stop()  # ← GEÄNDERT: Timer stoppen
            self.capture_photo()
    
    def capture_photo(self):
        """Capture photo from camera"""
        photo_path = self.camera.capture_photo()
        if photo_path:
            self.photos.append(photo_path)
        
        self.current_photo_index += 1
        
        if self.current_photo_index >= 3:
            # Series complete
            self.webcam_active = False
            if self.webcam:
                self.webcam.release()
            self.series_complete.emit(self.photos)
        else:
            # Nächstes Foto
            self.next_photo()
    
    def cleanup(self):
        """Cleanup: Stop timers and release resources"""
        self.timer.stop()
        self.webcam_active = False
        if self.webcam:
            self.webcam.release()
            self.webcam = None


class ReviewScreen(QWidget):
    """Review: 3 Fotos großformatig + Buttons"""
    
    retry_clicked = pyqtSignal()
    finish_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.photos = []
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet(f"background-color: {COLORS['bg_blau']};")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top Wave
        top_wave = OrganicWaveWidget(position="top", color=COLORS["gold"])
        main_layout.addWidget(top_wave)
        
        # Center: Fotos in Grid
        center_layout = QVBoxLayout()
        center_layout.setSpacing(20)
        center_layout.setContentsMargins(40, 40, 40, 40)
        
        # 3 Fotos horizontal anzeigen (großformatig)
        photos_layout = QHBoxLayout()
        photos_layout.setSpacing(20)
        
        self.photo_frames = []
        for i in range(3):
            frame = OrganicFrameWidget(parent=self)
            frame.setFixedSize(280, 350)
            photos_layout.addWidget(frame)
            self.photo_frames.append(frame)
        
        center_layout.addLayout(photos_layout)
        center_layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)
        button_layout.addStretch()
        
        # Retry Button
        retry_btn = QPushButton("↻ NOCHMAL")
        retry_btn.setFixedSize(160, 60)
        retry_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['coral']};
                border: 2px solid {COLORS['gold']};
                border-radius: 30px;
                color: {COLORS['creme']};
                font-size: 16px;
                font-weight: bold;
                font-family: Inria Serif;
            }}
            QPushButton:hover {{
                background-color: {COLORS['rosa']};
            }}
        """)
        retry_btn.clicked.connect(self.retry_clicked.emit)
        button_layout.addWidget(retry_btn)
        
        # Finish Button
        finish_btn = QPushButton("✓ BEENDEN")
        finish_btn.setFixedSize(160, 60)
        finish_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['gold']};
                border: 2px solid {COLORS['gold_dark']};
                border-radius: 30px;
                color: {COLORS['navy']};
                font-size: 16px;
                font-weight: bold;
                font-family: Inria Serif;
            }}
            QPushButton:hover {{
                background-color: {COLORS['gold_dark']};
            }}
        """)
        finish_btn.clicked.connect(self.finish_clicked.emit)
        button_layout.addWidget(finish_btn)
        
        button_layout.addStretch()
        center_layout.addLayout(button_layout)
        
        center_layout.addStretch()
        
        main_layout.addLayout(center_layout, 1)
        
        # Bottom Wave
        bottom_wave = OrganicWaveWidget(position="bottom", color=COLORS["rosa"])
        main_layout.addWidget(bottom_wave)
        
        self.setLayout(main_layout)
    
    def set_photos(self, photo_paths):
        """Setze die 3 Fotos für die Vorschau"""
        self.photos = photo_paths
        for i, photo_path in enumerate(photo_paths):
            if i < len(self.photo_frames):
                self.photo_frames[i].set_photo(photo_path)
    def cleanup(self):
        """Cleanup resources"""
        pass
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nora & Tilman - Fotobox")
        self.setGeometry(0, 0, 1280, 1024)
    
        # Screens MIT Parent!
        self.start_screen = StartScreen(self)       # ← Mit (self)
        self.photo_screen = PhotoSeriesScreen(self) # ← Mit (self)
        self.review_screen = ReviewScreen(self)     # ← Mit (self)
    
        # Verbinde Signale
        self.start_screen.start_clicked.connect(self.go_to_photo_series)
        self.photo_screen.series_complete.connect(self.go_to_review)
        self.review_screen.retry_clicked.connect(self.go_to_photo_series)
        self.review_screen.finish_clicked.connect(self.go_to_start)
        # Starte mit StartScreen
        self.setCentralWidget(self.start_screen)
    
    def go_to_photo_series(self):
        """Wechsel zu Photo Series Screen"""
        self.review_screen.cleanup()  # ← CLEANUP HINZUFÜGEN
        self.setCentralWidget(self.photo_screen)
        self.photo_screen.start_series()

    def go_to_review(self, photos):
        """Wechsel zu Review Screen"""
        self.photo_screen.cleanup()  # ← CLEANUP HINZUFÜGEN
        self.review_screen.set_photos(photos)
        self.setCentralWidget(self.review_screen)

    def go_to_start(self):
        """Zurück zum Start Screen"""
        self.review_screen.cleanup()  # ← CLEANUP HINZUFÜGEN
        self.setCentralWidget(self.start_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()  # Vollbildmodus
    sys.exit(app.exec_())