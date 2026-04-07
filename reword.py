"""
convert.py — chuyển file .docx câu hỏi trắc nghiệm sang .csv
Hỗ trợ 3 format thực tế trong bộ file:

  Format A (CĐ1..CĐ12):
    Câu hỏi → style='Heading 1' hoặc 'Heading 2'
    Đáp án  → style='List Paragraph', ilvl=1

  Format B (Bộ câu hỏi đáp án):
    Câu hỏi → style='Heading 1' hoặc style='Normal' với prefix "Câu N:"
    Đáp án  → style='List Paragraph', ilvl=0

  Format C (KDAPAN):
    Câu hỏi → style='Normal' với prefix "Câu N:"
    Đáp án  → style='Normal' với prefix "A. / B. / C. / D."

Đáp án đúng xác định qua highlight màu vàng trên đáp án (KHÔNG quan tâm highlight ở câu hỏi).
"""

import re
import csv
import glob
from docx import Document
from docx.oxml.ns import qn


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_ilvl(para):
    """List indent level từ XML Word (0 = câu hỏi, 1 = đáp án trong Format A/B)."""
    numPr = para._element.find(f'.//{qn("w:numPr")}')
    if numPr is None:
        return None
    ilvl = numPr.find(qn('w:ilvl'))
    return int(ilvl.get(qn('w:val'))) if ilvl is not None else None


def has_highlight(para):
    """True nếu bất kỳ run nào có màu highlight."""
    return any(
        r.font.highlight_color is not None and r.text.strip()
        for r in para.runs
    )


def clean_q(text):
    """Bỏ prefix 'Câu 1:' / '1.' khỏi câu hỏi."""
    return re.sub(r'^(Câu\s*)?\d+[\.\:]\s*', '', text).strip() or text


def clean_opt(text):
    """Bỏ prefix 'A.' / 'B)' … khỏi đáp án."""
    return re.sub(r'^[A-D][\.\)]\s*', '', text).strip()


def save_q(questions, current_q):
    """Thêm câu hỏi vào list nếu có ít nhất 2 đáp án."""
    if current_q and len(current_q['options']) >= 2:
        questions.append(current_q)


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_docx(file_path):
    doc = Document(file_path)
    questions = []
    current_q = None      # {'question': str, 'options': [(text, highlighted), ...]}

    for para in doc.paragraphs:
        text = para.text.strip()
        style = para.style.name if para.style else ''
        ilvl = get_ilvl(para)
        highlighted = has_highlight(para)

        if not text:
            continue

        # ── FORMAT C: Normal style với A/B/C/D prefix (KDAPAN) ──────────────
        is_abcd = bool(re.match(r'^[A-D][\.\)]\s*', text))
        is_cau = bool(re.match(r'^Câu\s*\d+[:\.]', text, re.IGNORECASE))

        if is_abcd and style not in ('List Paragraph',):
            if current_q is not None:
                current_q['options'].append((clean_opt(text), highlighted))
            continue

        if is_cau and style not in ('List Paragraph',):
            save_q(questions, current_q)
            current_q = {'question': clean_q(text), 'options': []}
            continue

        # ── FORMAT A/B: Heading style → câu hỏi ─────────────────────────────
        if style.startswith('Heading'):
            is_chapter_title = (
                '?' not in text
                and not re.match(r'^(Câu\s*)?\d+[:\.]', text, re.IGNORECASE)
            )
            if is_chapter_title:
                save_q(questions, current_q)
                current_q = None
                continue

            save_q(questions, current_q)
            current_q = {'question': clean_q(text), 'options': []}
            continue

        # ── List Paragraph: ilvl=0 → câu hỏi/đáp án, ilvl=1 → đáp án ───────
        if style == 'List Paragraph':
            if ilvl == 1:
                if current_q is not None:
                    current_q['options'].append((text, highlighted))

            elif ilvl == 0:
                if current_q is None:
                    # Format A: câu hỏi đầu tiên dùng List Paragraph ilvl=0
                    current_q = {'question': clean_q(text), 'options': []}
                else:
                    # Format B: đáp án ilvl=0 sau khi Heading đã set câu hỏi
                    current_q['options'].append((text, highlighted))

            else:
                if current_q is not None:
                    current_q['options'].append((text, highlighted))
            continue

        # ── Nối dòng: Body Text / Normal ─────────────────────────────────────
        if style in ('Body Text', 'Body Text 2', 'Normal') and current_q is not None:
            if not current_q['options']:
                current_q['question'] += ' ' + text
            else:
                last_txt, last_hi = current_q['options'][-1]
                current_q['options'][-1] = (last_txt + ' ' + text, last_hi or highlighted)

    save_q(questions, current_q)
    return questions


# ── Xuất CSV ──────────────────────────────────────────────────────────────────

def to_csv(questions, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['Question', 'A', 'B', 'C', 'D', 'Correct'])

        for q in questions:
            opts = list(q['options'])
            while len(opts) < 4:
                opts.append(('', False))

            correct_idx = next(
                (i for i, (_, h) in enumerate(opts) if h),
                0
            )

            writer.writerow([
                q['question'],
                opts[0][0], opts[1][0], opts[2][0], opts[3][0],
                ['A', 'B', 'C', 'D'][correct_idx],
            ])


# ── Batch ─────────────────────────────────────────────────────────────────────

def batch_convert():
    files = glob.glob('*.docx')
    if not files:
        print('Không tìm thấy file .docx nào trong thư mục!')
        return

    total = 0
    for file in files:
        print(f'Đang xử lý: {file} ...')
        try:
            questions = parse_docx(file)
            if not questions:
                print(f'[!] Không tìm thấy câu hỏi trong {file} — kiểm tra lại định dạng.')
                continue

            out = file.replace('.docx', '.csv')
            to_csv(questions, out)
            total += len(questions)
            print(f'[OK] {out}  ({len(questions)} câu)')
        except Exception as e:
            print(f'[ERR] Lỗi file {file}: {e}')

    print(f'\nHoan tat — tong {total} cau tu {len(files)} file.')


if __name__ == '__main__':
    batch_convert()