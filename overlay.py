import tkinter as tk
from tkinter import font

class SubtitleOverlay:
    def __init__(self, x, y, width, height):
        self.root = tk.Tk() if not tk._default_root else tk.Toplevel()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.boxes = []
        
        self.stable_font_spec = ("Segoe UI", 16, "bold")
        self.measure_font = font.Font(family="Segoe UI", size=16, weight="bold")
    
    def set_boxes(self, boxes, win_x, win_y):
        self.boxes = boxes

    def set_position(self, x, y, width, height):
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def update(self):
        self.canvas.delete("all")
        for (bx, by, bw, bh, text) in self.boxes:
            text_width = self.measure_font.measure(text)
            
            padding_x = 20
            card_height = 40
            
            self.canvas.create_rectangle(
                bx, by, 
                bx + text_width + padding_x, 
                by + card_height, 
                fill="#080808", 
                outline="#1f2937"
            )
            
            self.canvas.create_text(
                bx + (padding_x / 2), 
                by + (card_height / 2), 
                text=text, 
                fill="#FFFFFF", 
                anchor="w", 
                font=self.stable_font_spec
            )
            
        self.root.update_idletasks()

    def destroy(self):
        try:
            self.root.destroy()
        except:
            pass