import cv2
import numpy as np
import mss

def grab_region(x1, y1, x2, y2):
    monitor = {"top": int(y1), "left": int(x1), "width": int(x2 - x1), "height": int(y2 - y1)}
    
    with mss.mss() as sct:
        img_np = np.array(sct.grab(monitor))
        
    return cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

def preprocess_for_ocr(img):
    if img is None:
        return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    blur = cv2.GaussianBlur(resized, (3, 3), 0)
    
    _, mask = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY)
    
    inv_mask = cv2.bitwise_not(mask)
    
    return inv_mask