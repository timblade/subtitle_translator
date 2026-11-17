import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

if torch.cuda.is_available():
    torch.cuda.set_per_process_memory_fraction(0.5)  # 50% of 8 GB = 4 GB

class SubtitleTranslator:
    def __init__(self, model_name="facebook/nllb-200-distilled-600M"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.tok = AutoTokenizer.from_pretrained(model_name, src_lang="eng_Latn")
        self.model = (
            AutoModelForSeq2SeqLM.from_pretrained(model_name, torch_dtype=dtype)
            .to(self.device)
            .eval()
        )
        self.tr_id = self.tok.convert_tokens_to_ids("tur_Latn")
        self._cache = {}
        
        self.translate("Warmup")

    def translate(self, text):
        text = text.strip()
        if not text:
            return ""
        if text in self._cache:
            return self._cache[text]

        try:
            enc = self.tok(text, return_tensors="pt", truncation=True, max_length=50).to(self.device)
            with torch.inference_mode():
                out = self.model.generate(
                    **enc,
                    forced_bos_token_id=self.tr_id,
                    num_beams=1,
                    max_new_tokens=35,
                    max_length=None,           
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=2
                )
            result = self.tok.batch_decode(out, skip_special_tokens=True)[0]
        except Exception as e:
            print(f"Translation error: {e}")
            result = "[Translation Error]"

        self._cache[text] = result
        return result