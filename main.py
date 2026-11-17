import time
import re 
import threading
import queue
import tkinter as tk
from difflib import SequenceMatcher
from tkinter import ttk
import window_utils, capture, ocr, overlay
from translator import SubtitleTranslator

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

POLL_INTERVAL_SECONDS = 0.3

SUB_BAND_TOP = 0.75       
SUB_BAND_BOTTOM = 0.92    
BOX_HEIGHT = 60           
BOX_GAP = 5               
MAX_BOX_WIDTH = 900
MIN_TEXT_CHARS = 3        
SAME_TEXT_RATIO = 0.85    
DEBUG_SAVE_BAND = False   

def format_translation(text):
    if not text:
        return text
    
    text = re.sub(r'[^a-zA-Z0-9\süÜğĞıİşŞçÇöÖ]', '', text)
    
    text = re.sub(r'\s+', ' ', text)
    
    if text:
        text = text[0].upper() + text[1:]
        
    return text.strip()

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.target_language = "tr"
        self.root.title("Universal UI Translator")
        self.root.geometry("380x300")
        self.root.attributes("-topmost", True)

        self.hwnd = self.offset = self.ov = None
        self.stop_event = threading.Event()
        self.result_queue = queue.Queue()

        tk.Label(root, text="1. Select Window:").pack(padx=(5, 0), anchor="w")
        self.window_combo = ttk.Combobox(root, state="readonly", width=45)
        self.window_combo.pack(padx=5, pady=2)

        tk.Label(root, text="2. Controls:").pack(padx=(5, 0), anchor="w", pady=(5, 0))
        self.button_refresh = tk.Button(root, text="Refresh Windows", command=self.refresh_windows)
        self.button_refresh.pack(padx=5, pady=2, fill="x")

        self.start_btn = tk.Button(root, text="3. Start Auto-Translation", command=self.start_app, state="disabled", bg="#4CAF50", fg="white")
        self.start_btn.pack(padx=5, pady=5, fill="x")

        self.stop_btn = tk.Button(root, text="4. Stop Overlay", command=self.stop_app, state="disabled", bg="#f44336", fg="white")
        self.stop_btn.pack(padx=5, pady=2, fill="x")

        self.refresh_windows()

    def refresh_windows(self):
        self.windows = window_utils._enum_visible_windows()
        self.window_combo['values'] = [t for h, t in self.windows]
        if self.windows:
            self.window_combo.current(0)
            self.start_btn.config(state="normal")

    def capture_loop(self):
        translator = SubtitleTranslator()
        persistent_translations = {}
        active_boxes_map = {}

        last_text = ""
        last_translation = ""
        missing_count = 0
        debug_saved = False

        while not self.stop_event.is_set():
            if not window_utils.is_window_valid(self.hwnd):
                break

            wl, wt, wr, wb = window_utils.get_window_rect(self.hwnd)
            w, h = wr - wl, wb - wt

            band_top_rel = int(h * SUB_BAND_TOP)
            band_bottom_rel = int(h * SUB_BAND_BOTTOM)
            img = capture.grab_region(wl, wt + band_top_rel, wr, wt + band_bottom_rel)

            if DEBUG_SAVE_BAND and not debug_saved:
                try:
                    import cv2
                    cv2.imwrite("debug_band.png", img)
                    print("Saved debug_band.png (this is exactly what OCR reads)")
                except Exception as e:
                    print(f"Could not save debug image: {e}")
                debug_saved = True

            preprocessed = capture.preprocess_for_ocr(img)
            raw_text = ocr.extract_text(preprocessed)
            
            if raw_text:
                import re
                raw_text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', raw_text)
                
            cleaned = " ".join(raw_text.split()) if raw_text else ""
            letter_count = sum(c.isalpha() for c in cleaned)

            if len(cleaned) >= MIN_TEXT_CHARS and letter_count >= 2:
                missing_count = 0
                
                if not last_text or SequenceMatcher(None, cleaned, last_text).ratio() < 0.95:
                    last_text = cleaned
                    if cleaned not in persistent_translations:
                        raw_translation = translator.translate(cleaned)
                        persistent_translations[cleaned] = format_translation(raw_translation)
                    last_translation = persistent_translations[cleaned]
            else:
                missing_count += 1
                if missing_count >= 2:
                    last_text = ""
                    last_translation = ""

            if last_translation:
                estimated_text_width = len(last_translation) * 11 
                box_w = min(estimated_text_width + 40, MAX_BOX_WIDTH) 
                box_x = (w - box_w) // 2 
                
                box_y = band_top_rel - 45
                
                self.result_queue.put(("single", [(box_x, box_y, box_w, BOX_HEIGHT, last_translation)]))
            else:
                self.result_queue.put(("single", []))

            time.sleep(POLL_INTERVAL_SECONDS)

    def update_overlay(self):
        if self.stop_event.is_set():
            return
        try:
            mode, data = self.result_queue.get_nowait()
            if self.ov:
                wl, wt, wr, wb = window_utils.get_window_rect(self.hwnd)
                self.ov.set_boxes(data, wl, wt)
        except queue.Empty:
            pass

        if self.ov:
            self.ov.update()
        self.root.after(30, self.update_overlay)

    def start_app(self):
        self.start_btn.config(state="disabled", text="Running...")
        self.stop_btn.config(state="normal")
        self.stop_event.clear()
        self.hwnd = self.windows[self.window_combo.current()][0]
        window_utils.bring_to_front(self.hwnd)
        time.sleep(0.3)

        wl, wt, wr, wb = window_utils.get_window_rect(self.hwnd)
        w, h = wr - wl, wb - wt

        self.ov = overlay.SubtitleOverlay(x=wl, y=wt, width=w, height=h)
        threading.Thread(target=self.capture_loop, daemon=True).start()
        self.update_overlay()

    def stop_app(self):
        self.stop_event.set()
        if self.ov:
            self.ov.destroy()
            self.ov = None
        self.start_btn.config(state="normal", text="3. Start Auto-Translation")
        self.stop_btn.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()