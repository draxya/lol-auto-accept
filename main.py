import sys
import time
import numpy as np
import cv2
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox, Scale, IntVar, StringVar
from threading import Thread
import keyboard
import gc
import os
import json
import PIL
from PIL import Image

__version__ = "1.1.0"
APP_NAME = "Be Right Back"


def resource_path(relative_path):
    """PyInstaller ile çalışırken kaynakların yolunu bul"""
    try:
        # PyInstaller creates a temp folder at _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

try:
    import pytesseract

    # Birden fazla potansiyel Tesseract konumunu deneyelim
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]

    # Tesseract'ı bulmaya çalış
    TESSERACT_AVAILABLE = False
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            TESSERACT_AVAILABLE = True
            print(f"Tesseract bulundu: {path}")
            break

    if not TESSERACT_AVAILABLE:
        print("Tesseract bulunamadı!")
except ImportError:
    TESSERACT_AVAILABLE = False
    print("pytesseract modülü bulunamadı!")

# Desteklenen diller ve her dildeki aranacak metinler
SUPPORTED_LANGUAGES = {
    "Türkçe": ["kabul et", "kabul", "onayla", "hazır", "tamam", "eşleşme bulundu", "karşılaşma bulundu"],
    "English": ["accept", "ready", "confirm", "ok", "match found", "match accepted"],
    "Deutsch": ["akzeptieren", "bereit", "bestätigen", "spiel gefunden"],
    "Français": ["accepter", "prêt", "confirmer", "partie trouvée"],
    "Español": ["aceptar", "listo", "confirmar", "partida encontrada"],
    "Русский": ["принять", "готов", "подтвердить", "матч найден"],
    "한국어": ["수락", "준비", "확인", "매치 찾음"],  # Korean
    "日本語": ["承認", "準備完了", "確認", "マッチが見つかりました"],  # Japanese
    "中文": ["接受", "准备", "确认", "比赛已找到"]  # Chinese
}

# Farklı ekran çözünürlükleri için sabit koordinatlar
FIXED_COORDS = {
    "1080p": (956, 712)  # 1920x1080 için kabul et butonu koordinatı
}


class MatchDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("League Match Acceptor")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)  # Always on top

        # Set window size and position
        self.root.geometry("320x350")
        self.root.configure(bg="#f0f0f0")

        # Variables
        self.detecting = False
        self.detection_thread = None
        self.rift_image = None
        self.tft_image = None
        self.screen_width, self.screen_height = pyautogui.size()
        self.capture_region = (0, 0, self.screen_width, self.screen_height)
        self.threshold = 0.6
        self.detection_interval = 0.5  # Default scanning interval in seconds
        self.selected_language = StringVar(value="")  # Selected language
        self.use_ocr = IntVar(value=1 if TESSERACT_AVAILABLE else 0)  # Use OCR if available
        self.use_image = IntVar(value=1)  # Use image detection by default
        self.use_fixed_coords = IntVar(value=0)  # Use fixed coordinates for 1080p
        self.settings_file = "lol_acceptor_settings.json"
        self.success_count = 0

        # Fixed shortcuts
        self.start_key = "F6"
        self.stop_key = "F7"

        # Check if current resolution is 1080p
        self.is_1080p = (self.screen_width == 1920 and self.screen_height == 1080)

        # Create UI
        self.create_ui()

        # Load settings
        self.load_settings()

        # Load target images
        self.load_target_images()

        # Check Tesseract
        self.check_tesseract()

        # Now that UI is created, update language display
        self.update_language_display()

        # Show language selection if not already set
        if not self.selected_language.get():
            self.show_language_selector()

        # Register keyboard shortcuts
        self.register_shortcuts()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                    self.selected_language.set(settings.get("language", ""))
                    self.detection_interval = settings.get("interval", 0.5)
                    self.use_ocr.set(settings.get("use_ocr", 1 if TESSERACT_AVAILABLE else 0))
                    self.use_image.set(settings.get("use_image", 1))
                    self.use_fixed_coords.set(settings.get("use_fixed_coords", 0))
                    print(f"Ayarlar yüklendi: {settings}")
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")

    def save_settings(self):
        try:
            settings = {
                "language": self.selected_language.get(),
                "interval": self.detection_interval,
                "use_ocr": self.use_ocr.get(),
                "use_image": self.use_image.get(),
                "use_fixed_coords": self.use_fixed_coords.get()
            }
            with open(self.settings_file, "w") as f:
                json.dump(settings, f)
            print(f"Ayarlar kaydedildi: {settings}")
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")

    def show_language_selector(self):
        lang_window = tk.Toplevel(self.root)
        lang_window.title("League of Legends Dil Seçimi")
        lang_window.geometry("300x400")
        lang_window.resizable(False, False)
        lang_window.transient(self.root)
        lang_window.grab_set()

        ttk.Label(
            lang_window,
            text="League of Legends'ın dilini seçin:",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        lang_frame = ttk.Frame(lang_window)
        lang_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Language radio buttons
        for lang in SUPPORTED_LANGUAGES.keys():
            ttk.Radiobutton(
                lang_frame,
                text=lang,
                value=lang,
                variable=self.selected_language
            ).pack(anchor=tk.W, pady=3)

        def on_ok():
            if not self.selected_language.get():
                messagebox.showwarning("Uyarı", "Lütfen bir dil seçin!")
                return
            self.save_settings()
            # UI is already created at this point, so update is safe
            self.update_language_display()
            lang_window.destroy()

        ttk.Button(
            lang_window,
            text="Tamam",
            command=on_ok
        ).pack(pady=10)

        # Set default if not already set
        if not self.selected_language.get() and "Türkçe" in SUPPORTED_LANGUAGES:
            self.selected_language.set("Türkçe")

        # Wait for the window to close
        self.root.wait_window(lang_window)

    def check_tesseract(self):
        if not TESSERACT_AVAILABLE:
            self.use_ocr.set(0)
            print("Tesseract bulunamadı, OCR özelliği devre dışı bırakıldı.")

    def load_target_images(self):
        """Load both Rift and TFT reference images"""
        try:
            # Gömülü kaynaklardan yüklemeyi dene
            rift_path = resource_path("target_image_rift.png")
            tft_path = resource_path("target_image_tft.png")

            # Summoner's Rift image
            if os.path.exists(rift_path):
                self.rift_image = cv2.imread(rift_path)
                print("Summoner's Rift görüntüsü yüklendi.")
            else:
                print("target_image_rift.png bulunamadı.")

            # Load TFT image
            if os.path.exists(tft_path):
                self.tft_image = cv2.imread(tft_path)
                print("TFT görüntüsü yüklendi.")
            else:
                print("target_image_tft.png bulunamadı.")

            # Check if at least one image loaded
            if self.rift_image is None and self.tft_image is None:
                self.use_image.set(0)
                print("Hiçbir referans görüntü yüklenemedi.")

            # Başarılı yüklenen görüntü varsa, görüntü tanımayı etkinleştir
            if self.rift_image is not None or self.tft_image is not None:
                self.use_image.set(1)
        except Exception as e:
            self.use_image.set(0)
            print(f"Referans görüntü yüklenirken hata: {e}")

    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10))
        style.configure("TLabel", font=("Arial", 10))
        style.configure("Status.TLabel", font=("Arial", 11, "bold"))
        style.configure("Success.TLabel", font=("Arial", 11, "bold"), foreground="green")

        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(
            status_frame,
            text="Durum: Bekliyor",
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.LEFT)

        # Language info
        self.lang_info_label = ttk.Label(
            main_frame,
            text="Seçili Dil: -"
        )
        self.lang_info_label.pack(fill=tk.X, pady=(0, 5))

        # Change language button
        ttk.Button(
            main_frame,
            text="Dil Değiştir",
            command=self.show_language_selector
        ).pack(fill=tk.X, pady=(0, 10))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.start_button = ttk.Button(
            button_frame,
            text=f"Başlat (F6)",
            command=self.start_detection
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.stop_button = ttk.Button(
            button_frame,
            text=f"Durdur (F7)",
            command=self.stop_detection,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Ayarlar")
        settings_frame.pack(fill=tk.X, pady=10)

        # Detection methods
        methods_frame = ttk.Frame(settings_frame)
        methods_frame.pack(fill=tk.X, pady=5)

        # Detection methods checkboxes
        ttk.Checkbutton(
            methods_frame,
            text="Görüntü Tanıma (target_image_rift/tft.png gerekli)",
            variable=self.use_image,
            onvalue=1,
            offvalue=0,
            command=self.save_settings
        ).pack(anchor=tk.W, padx=10, pady=2)

        # OCR checkbox
        ocr_checkbox = ttk.Checkbutton(
            methods_frame,
            text="Metin Tanıma (OCR) - Tesseract gerekli",
            variable=self.use_ocr,
            onvalue=1,
            offvalue=0,
            command=self.save_settings
        )
        ocr_checkbox.pack(anchor=tk.W, padx=10, pady=2)

        if not TESSERACT_AVAILABLE:
            ocr_checkbox.config(state=tk.DISABLED)

        # Fixed coordinates for 1080p (only show if resolution is 1920x1080)
        if self.is_1080p:
            ttk.Checkbutton(
                methods_frame,
                text="1080p Sabit Pencere Modu (956, 712)",
                variable=self.use_fixed_coords,
                onvalue=1,
                offvalue=0,
                command=self.save_settings
            ).pack(anchor=tk.W, padx=10, pady=2)

        # Scan interval slider
        interval_frame = ttk.Frame(settings_frame)
        interval_frame.pack(fill=tk.X, pady=5)

        ttk.Label(interval_frame, text="Tarama Aralığı (saniye):").pack(anchor=tk.W)

        self.interval_slider = Scale(
            interval_frame,
            from_=0.1,
            to=3.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            length=280,
            variable=tk.DoubleVar(value=self.detection_interval)
        )
        self.interval_slider.pack(fill=tk.X)
        self.interval_slider.bind("<ButtonRelease-1>", lambda _: self.save_settings())

        # Success count
        self.success_label = ttk.Label(
            main_frame,
            text="Başarılı Tıklama: 0",
            style="Success.TLabel"
        )
        self.success_label.pack(fill=tk.X, pady=(10, 0))

        # Debug info and image status
        images_loaded = []
        if hasattr(self, 'rift_image') and self.rift_image is not None:
            images_loaded.append("Rift")
        if hasattr(self, 'tft_image') and self.tft_image is not None:
            images_loaded.append("TFT")

        image_status = "Yüklü Görüntüler: " + (", ".join(images_loaded) if images_loaded else "Yok")

        self.debug_label = ttk.Label(main_frame, text=f"Ekran: {self.screen_width}x{self.screen_height}")
        self.debug_label.pack(fill=tk.X, pady=(5, 0))

        self.image_status_label = ttk.Label(main_frame, text=image_status)
        self.image_status_label.pack(fill=tk.X, pady=(5, 0))

    def update_language_display(self):
        if hasattr(self, 'lang_info_label'):
            self.lang_info_label.config(text=f"Seçili Dil: {self.selected_language.get()}")

    def register_shortcuts(self):
        # Clear existing hotkeys
        try:
            keyboard.unhook_all()
        except:
            pass

        # Register fixed hotkeys
        keyboard.add_hotkey(self.start_key, self.start_detection)
        keyboard.add_hotkey(self.stop_key, self.stop_detection)

    def find_image_on_screen(self):
        """Ekranda kabul butonunu bul - hem Rift hem de TFT görüntülerini kontrol et"""
        if not self.use_image.get():
            return False, None

        if self.rift_image is None and self.tft_image is None:
            return False, None

        try:
            # Ekran görüntüsü al
            screenshot = pyautogui.screenshot()
            screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Summoner's Rift görüntüsünü kontrol et
            if self.rift_image is not None:
                found, position = self._check_template(screenshot_np, self.rift_image)
                if found:
                    return True, position

            # TFT görüntüsünü kontrol et
            if self.tft_image is not None:
                found, position = self._check_template(screenshot_np, self.tft_image)
                if found:
                    return True, position

            return False, None
        except Exception as e:
            print(f"Görüntü tanıma hatası: {e}")
            return False, None
        finally:
            gc.collect()

    def _check_template(self, screenshot, template):
        """Belirli bir şablonu ekranda ara"""
        # Template boyutlarını al
        template_height, template_width = template.shape[:2]

        # Farklı ölçeklerde dene
        for scale in np.linspace(0.7, 1.3, 5):
            # Şablonu yeniden boyutlandır
            resized_template = cv2.resize(template,
                                          (int(template_width * scale),
                                           int(template_height * scale)))

            # Şablon ekrandan büyükse atla
            if (resized_template.shape[0] > screenshot.shape[0] or
                    resized_template.shape[1] > screenshot.shape[1]):
                continue

            # Template matching yap
            result = cv2.matchTemplate(screenshot, resized_template, cv2.TM_CCOEFF_NORMED)

            # Eşik değerini aş
            loc = np.where(result >= self.threshold)

            # Eşleşme bulundu mu?
            if len(loc[0]) > 0:
                # En iyi eşleşmeyi bul
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                # Butonun merkezi
                h, w = resized_template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2

                print(f"Görüntü eşleşmesi bulundu! Benzerlik: {max_val:.4f}, Konum: ({center_x}, {center_y})")
                return True, (center_x, center_y)

        return False, None

    def find_accept_button_with_ocr(self):
        """OCR ile ekrandaki "Accept", "Kabul Et" vb. butonları seçilen dile göre arar"""
        if not TESSERACT_AVAILABLE or self.use_ocr.get() == 0:
            return False, None

        selected_lang = self.selected_language.get()
        if not selected_lang or selected_lang not in SUPPORTED_LANGUAGES:
            return False, None

        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()

            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

            # Apply some preprocessing to improve OCR
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

            # Use simple OCR to find text (faster and more reliable than image_to_data)
            text = pytesseract.image_to_string(binary).lower()

            # Get keywords for selected language
            keywords = SUPPORTED_LANGUAGES[selected_lang]

            # Check if any keyword is in the text
            for keyword in keywords:
                if keyword.lower() in text:
                    print(f"OCR Anahtar Kelime Bulundu: '{keyword}'")

                    # Further refine search using image_to_data for position
                    try:
                        data = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT)

                        # Look for the specific keyword that was found
                        for i, word in enumerate(data['text']):
                            if not word.strip():
                                continue

                            if keyword.lower() in word.lower():
                                # Get the bounding box and return center
                                x = data['left'][i]
                                y = data['top'][i]
                                w = data['width'][i]
                                h = data['height'][i]

                                center_x = x + w // 2
                                center_y = y + h // 2
                                print(f"Pozisyon: ({center_x}, {center_y})")
                                return True, (center_x, center_y)
                    except Exception as e:
                        print(f"Pozisyon belirleme hatası: {e}")

                    # Fallback: OCR text found but position determination failed
                    # Just click on the center-bottom part of the screen where accept buttons typically are
                    center_x = self.screen_width // 2
                    center_y = int(self.screen_height * 0.7)  # Screen's bottom part
                    print(f"Konum bulunamadı, varsayılan konuma tıklanıyor: ({center_x}, {center_y})")
                    return True, (center_x, center_y)

            return False, None
        except Exception as e:
            print(f"OCR hatası: {e}")
            return False, None
        finally:
            gc.collect()

    def start_detection(self):
        if self.detecting:
            return

        # Check if language is selected
        if not self.selected_language.get():
            messagebox.showwarning(
                "Uyarı",
                "Lütfen önce bir dil seçin!"
            )
            self.show_language_selector()
            if not self.selected_language.get():
                return

        # At least one detection method must be enabled or fixed mode enabled
        if self.use_fixed_coords.get() == 0 and self.use_image.get() == 0 and (
                not TESSERACT_AVAILABLE or self.use_ocr.get() == 0):
            messagebox.showwarning(
                "Uyarı",
                "En az bir algılama yöntemi seçmelisiniz!\n"
                "- Görüntü Tanıma için kayıtlı görüntü gerekli\n"
                "- OCR için Tesseract yükleyin\n"
                "- 1080p monitörlerde 'Sabit Pencere Modu'nu kullanabilirsiniz"
            )
            return

        self.detecting = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Durum: Aktif")

        # Update detection interval
        self.detection_interval = self.interval_slider.get()

        # Start detection in a separate thread
        self.detection_thread = Thread(target=self.detect_loop, daemon=True)
        self.detection_thread.start()

    def stop_detection(self):
        if not self.detecting:
            return

        self.detecting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Durum: Durduruldu")

        # Force garbage collection to free up memory
        gc.collect()

    def detect_loop(self):
        while self.detecting:
            found = False
            click_pos = None

            # 1080p Sabit Pencere Modu - her zaman öncelikli
            if self.is_1080p and self.use_fixed_coords.get() == 1:
                found = True
                click_pos = FIXED_COORDS["1080p"]
                self.status_label.config(text="Durum: 1080p Sabit Mod Kullanılıyor")

            # Görüntü tanıma (hem Rift hem de TFT)
            if not found and self.use_image.get() == 1:
                found, click_pos = self.find_image_on_screen()
                if found:
                    self.status_label.config(text="Durum: Görüntü Bulundu!")

            # OCR
            if not found and TESSERACT_AVAILABLE and self.use_ocr.get() == 1:
                found, click_pos = self.find_accept_button_with_ocr()
                if found:
                    self.status_label.config(text=f"Durum: OCR ile Bulundu! ({self.selected_language.get()})")

            # Tıkla!
            if found and click_pos:
                pyautogui.click(click_pos[0], click_pos[1])
                print(f"Tıklama: {click_pos}")

                # Başarılı sayacını güncelle
                self.success_count += 1
                self.root.after(0, lambda: self.success_label.config(text=f"Başarılı Tıklama: {self.success_count}"))

                # Ses çal (opsiyonel)
                try:
                    # Windows'ta ses çalmak için
                    import winsound
                    winsound.MessageBeep()
                except:
                    pass

                time.sleep(2)  # Başarılı tıklamadan sonra biraz daha uzun bekle
            else:
                # No match found, wait for the next check
                time.sleep(self.detection_interval)

            # Belleği boşalt
            gc.collect()


# Main function
def main():
    root = tk.Tk()
    app = MatchDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()