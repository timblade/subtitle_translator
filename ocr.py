import re
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_boxes(img):
    if img is None:
        return []
    
    data = pytesseract.image_to_data(img, config='--psm 11', output_type=pytesseract.Output.DICT)
    
    line_groups = {}
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        conf = int(data['conf'][i])
        
        if conf > 60 and len(text) > 0 and any(c.isalnum() for c in text):
            key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
            if key not in line_groups:
                line_groups[key] = []
            line_groups[key].append((data['left'][i], data['top'][i], data['width'][i], data['height'][i], text))
    
    results = []
    for key, words in line_groups.items():
        words.sort(key=lambda w: w[0])
        full_text = " ".join([w[4] for w in words])
        
        min_x = words[0][0]
        min_y = min(w[1] for w in words)
        max_right = max(w[0] + w[2] for w in words)
        max_bottom = max(w[1] + w[3] for w in words)
        
        w_box = max_right - min_x
        h_box = max_bottom - min_y
        
        if len(full_text.strip()) > 1:
            results.append((full_text, (min_x, min_y, w_box, h_box)))
            
    return results

def extract_text(img):
    if img is None:
        return ""
    
    data = pytesseract.image_to_data(img, config='--psm 6', output_type=pytesseract.Output.DICT)
    
    valid_words = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        
        try:
            conf = int(float(data['conf'][i]))
        except (ValueError, TypeError):
            conf = 0
            
        if conf > 60 and len(text) > 0:
            valid_words.append(text)
            
    return " ".join(valid_words)