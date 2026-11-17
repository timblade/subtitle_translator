# GamerEngineers Universal Subtitle Translator

A real-time, completely offline English-to-Turkish OCR subtitle translator designed for gaming and video streaming. It captures specific screen regions, processes text using Tesseract OCR, and translates it instantly using a local AI model (Hugging Face NLLB) with zero API costs or network latency.

## ⚠️ Required Prerequisites

**Tesseract OCR MUST be installed on your PC before launching this app.** The application relies on this engine to read text from your screen.

1. Download the Windows installer for Tesseract OCR: [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and proceed with the standard installation.
3. **CRITICAL:** The app hardcodes the Tesseract path. You must install it to the default directory so that this exact file path exists:
   `C:\Program Files\Tesseract-OCR\tesseract.exe`

---

## 🚀 How to Run (Pre-Packaged .exe)

If you are using the compiled `GamerEngineers_Translator` application folder:

1. Ensure Tesseract OCR is installed (see above).
2. Ensure you have an active internet connection for the **very first launch**. (The app needs to download the `facebook/nllb-200-distilled-600M` AI translation model to your local cache once. It runs completely offline after this).
3. Open the `dist/GamerEngineers_Translator` folder and double-click **`GamerEngineers_Translator.exe`**.
4. **Windows 11 Security Note:** Because this is a locally compiled application, Windows "Smart App Control" or Microsoft Defender may block it. To run the app:
   * Right-click the `.exe` -> **Properties** -> Check **Unblock** at the bottom of the General tab -> **Apply**.
   * *If the Unblock box is missing:* Turn off **Smart App Control** in your Windows settings.

---

## 💻 How to Run (From Source)

If you are running the raw Python files (e.g., via VS Code):

1. Install **Python 3.10 or newer**.
2. Install the required Python dependencies:
   ```bash
   pip install torch transformers mss opencv-python pytesseract pywin32