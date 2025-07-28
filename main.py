#!/usr/bin/env python3
import os
import fitz
import json
import re
import torch
from langdetect import detect
from transformers import T5Tokenizer, T5ForConditionalGeneration

model_name = 'google/flan-t5-small'
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(
    model_name,
    load_in_8bit=True,
    device_map='auto'
)

def generate_heading(text: str) -> str:
    lang = detect(text)
    prompt = f"Generate a title in {lang}: " + text.replace('\n', ' ')
    inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    outputs = model.generate(
        **inputs,
        max_new_tokens=30,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=2
    )
    heading = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    return heading or text.split('.',1)[0]

def explicit_numbering_level(para: str) -> int:
    m = re.match(r'^(\d+(?:\.\d+)*)\s+', para)
    return min(m.group(1).count('.') + 1, 3) if m else 0

def process(pdf_path: str):
    doc = fitz.open(pdf_path)
    outline = []
    for idx in range(doc.page_count):
        page_num = idx + 1
        raw = doc[idx].get_text('text')
        paras = [p.strip() for p in re.split(r'\n\s*\n+', raw) if p.strip()]
        if not paras:
            continue
        # H1
        if explicit_numbering_level(paras[0]) == 1:
            h1 = paras[0]
        else:
            h1 = generate_heading(raw)
        outline.append({'level': 'H1', 'text': h1, 'page': page_num})
        # H2 / H3
        for p in paras:
            lvl = explicit_numbering_level(p)
            if lvl == 1:
                continue
            if lvl == 2:
                outline.append({'level': 'H2', 'text': p, 'page': page_num})
            elif lvl == 3:
                outline.append({'level': 'H3', 'text': p, 'page': page_num})
            else:
                summary = generate_heading(p)
                outline.append({'level': 'H2', 'text': summary, 'page': page_num})
    return outline

def main(input_dir: str = '/app/input', output_dir: str = '/app/output'):
    os.makedirs(output_dir, exist_ok=True)
    aggregated = {}
    for fname in os.listdir(input_dir):
        if not fname.lower().endswith('.pdf'):
            continue
        path = os.path.join(input_dir, fname)
        base = os.path.splitext(fname)[0]
        outline = process(path)
        out_file = os.path.join(output_dir, f'{base}.json')
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump({'outline': outline}, f, indent=4, ensure_ascii=False)
        aggregated[base] = outline
    # aggregated output.json
    agg_path = os.path.join(output_dir, 'output.json')
    with open(agg_path, 'w', encoding='utf-8') as f:
        json.dump(aggregated, f, indent=4, ensure_ascii=False)
    print('Batch processing complete.')

if __name__ == '__main__':
    main()
