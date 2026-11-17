import tkinter as tk

def select_region_on_screen():
   
    result = {"rect": None}

    root = tk.Toplevel()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.25)          
    root.attributes("-topmost", True)
    root.configure(bg="gray")
    root.config(cursor="cross")

    canvas = tk.Canvas(root, bg="gray", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    canvas.create_text(
        root.winfo_screenwidth() // 2, 40,
        text="Drag a box over the subtitle area, then release. Press ESC to cancel.",
        fill="white", font=("Segoe UI", 16, "bold"),
    )

    start = {}
    rect_id = {"id": None}

    def on_press(event):
        start["x"], start["y"] = event.x, event.y
        if rect_id["id"] is not None:
            canvas.delete(rect_id["id"])
        rect_id["id"] = canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="red", width=3
        )

    def on_drag(event):
        canvas.coords(rect_id["id"], start["x"], start["y"], event.x, event.y)

    def on_release(event):
        x0, y0 = start["x"], start["y"]
        x1, y1 = event.x, event.y
        left, right = sorted((x0, x1))
        top, bottom = sorted((y0, y1))
        if right - left < 5 or bottom - top < 5:
            return  
        result["rect"] = (left, top, right, bottom)
        root.destroy()

    def on_escape(_event):
        result["rect"] = None
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", on_escape)

    root.wait_window()
    
    return result["rect"]