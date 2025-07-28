import os
import json
import fitz  # PyMuPDF
import re
from collections import defaultdict

def is_valid_heading(text, font_size, position_y, flags):
    if len(text.strip()) == 0:
        return False
    if len(text.split()) < 2:
        return False
    if position_y > 200:
        return False
    stopwords = ["Page", "Figure", "Table", "Author", "Editor"]
    if any(sw.lower() in text.lower() for sw in stopwords):
        return False
    if not re.match(r'^(Chapter \d+|\d+(\.\d+)*|[A-Z])', text):
        return False
    if flags != 20:  # usually bold
        return False
    return True

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    font_stats = defaultdict(list)
    headings = []
    title = ""

    for page in doc:
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            if 'lines' not in b:
                continue
            for l in b['lines']:
                for span in l['spans']:
                    font_size = round(span['size'], 1)
                    font_stats[font_size].append(span['text'].strip())

    sorted_fonts = sorted(font_stats.items(), key=lambda x: -x[0])
    if sorted_fonts:
        title_candidates = [t for t in sorted_fonts[0][1] if len(t.split()) >= 2]
        if title_candidates:
            title = title_candidates[0]

    levels = {}
    for i, (fs, _) in enumerate(sorted_fonts[:3]):
        levels[fs] = f"H{i+1}"

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            if 'lines' not in b:
                continue
            for l in b['lines']:
                for span in l['spans']:
                    text = span['text'].strip()
                    font_size = round(span['size'], 1)
                    y0 = span['bbox'][1]
                    flags = span['flags']

                    if text == title:
                        continue  # Avoid adding title to outline

                    if font_size in levels and is_valid_heading(text, font_size, y0, flags):
                        headings.append({
                            "level": levels[font_size],
                            "text": text,
                            "page": page_num + 1
                        })

    return title, headings

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            title, outline = extract_outline(pdf_path)
            json_output = {
                "title": title,
                "outline": outline
            }
            output_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, indent=2)

if __name__ == "__main__":
    main()
