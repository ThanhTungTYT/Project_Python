import os
from transformers import pipeline

class comment_filter:
    def __init__(self):
        self.classifier = pipeline('text2text-generation', model='tarudesu/ViHateT5-base-HSD', framework='pt')

        current_dir = os.path.dirname(__file__)
        self.badword_file = os.path.join(current_dir, 'datasets', 'badword.txt') 

        self.badwords = self.load_badwords()

    def load_badwords(self):
        words = []
        try:
            with open(self.badword_file, 'r', encoding='utf-8') as f:
                words = [line.strip().lower() for line in f if line.strip() and not line.strip().startswith('#')]
            print(f"Loaded {len(words)} bad words.")
        except FileNotFoundError:
            print(f"File not found: {self.badword_file}")
        return words
    
    def is_toxic(self, comment):
        if not comment:
            return False, "Rỗng"
        
        text_lower = comment.lower()
        for word in self.badwords:
            if word in text_lower:
                return True, "Chứa từ ngữ không hợp lệ"
        try:
            input_text = f"hate-speech-detection: {comment}"
            result = self.classifier(input_text)[0]
            label = result['generated_text'].strip().upper()
            print(f"[AI CHECK] Input: '{comment}' -> Label: {label}")
            if label in ['OFFENSIVE', 'HATE']:
                return True, "Ngôn từ vi phạm tiêu chuẩn cộng đồng (AI)"
        except Exception as e:
            print(f"Lỗi phân tích cảm xúc: {e}")
        return False, "Hợp lệ"

filter_engine = comment_filter()