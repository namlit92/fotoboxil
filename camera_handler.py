import subprocess
import os
from datetime import datetime

class CameraHandler:
    def __init__(self):
        self.output_dir = os.path.expanduser("~/Desktop/Fotobox_Nora_Tilman")
        self.create_output_directory()
    
    def create_output_directory(self):
        """Erstellt das Ausgabeverzeichnis, falls es nicht existiert"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✅ Verzeichnis erstellt: {self.output_dir}")
    
    def capture_image(self):
        """
        Macht ein Foto mit der Canon 450D via gphoto2
        Speichert mit Timestamp im Dateinamen
        Gibt Dateipfad zurück oder None bei Fehler
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Nora_Tilman_{timestamp}.jpg"
        
        try:
            # gphoto2 Command
            cmd = [
                "gphoto2",
                "--capture-image-and-download",
                f"--filename={os.path.join(self.output_dir, filename)}"
            ]
            
            print(f"🔷 Starte Fotoaufnahme: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                print(f"❌ gphoto2 Fehler: {result.stderr}")
                return None
            
            file_path = os.path.join(self.output_dir, filename)
            
            # Überprüfe, ob Datei existiert
            if os.path.exists(file_path):
                print(f"✅ Foto gespeichert: {file_path}")
                return file_path
            else:
                print(f"❌ Foto-Datei nicht gefunden: {file_path}")
                return None
        
        except subprocess.TimeoutExpired:
            print("❌ gphoto2 Timeout - Kamera antwortet nicht")
            return None
        except Exception as e:
            print(f"❌ Fehler beim Fotografieren: {e}")
            return None
    
    def check_camera_status(self):
        """Überprüft, ob die Kamera erreichbar ist"""
        try:
            result = subprocess.run(
                ["gphoto2", "--auto-detect"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "Canon" in result.stdout or "450D" in result.stdout:
                print("✅ Canon 450D gefunden")
                return True
            else:
                print("❌ Kamera nicht erkannt")
                return False
        except Exception as e:
            print(f"❌ Fehler beim Prüfen der Kamera: {e}")
            return False
