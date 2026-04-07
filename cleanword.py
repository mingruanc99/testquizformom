import re
import csv
import glob
import os
from docx import Document

def is_numbered(para):
    """Kiểm tra xem đoạn văn có thuộc tính 'Số tự động' trong XML không"""
    # Soi vào thuộc tính numPr của Word
    return bool(para._element.xpath('./w:pPr/w:numPr'))

def parse_docx(file_path):
    doc = Document(file_path)
    questions = []
    current_q = None
    q_counter = 0

    for para in doc.paragraphs:
        # Lấy text và kiểm tra Numbering
        text = para.text.strip()
        is_num = is_numbered(para)
        
        if not text and not is_num: continue

        # 1. NHẬN DIỆN ĐÁP ÁN TRƯỚC (Dựa vào text cứng A. B. C. D.)
        # Nếu dòng đó bắt đầu bằng A. hoặc B. hoặc C. hoặc D.
        is_option = re.match(r"^[A-D][\.\)]", text)
        
        if is_option and current_q:
            is_highlighted = False
            for run in para.runs:
                if run.font.highlight_color and run.text.strip():
                    is_highlighted = True
                    break
            
            clean_option = re.sub(r"^[A-D][\.\)]\s*", "", text)
            current_q["options"].append((clean_option, is_highlighted))

        # 2. NHẬN DIỆN CÂU HỎI (Nếu là Numbering và KHÔNG PHẢI đáp án)
        elif is_num or re.match(r"^\d+\.", text):
            # Lưu câu trước đó nếu có
            if current_q:
                questions.append(current_q)
            
            q_counter += 1
            # Nếu para.text trống do Word giấu số, ta tự điền số thứ tự
            display_text = text if text else f"Câu hỏi {q_counter}"
            
            current_q = {
                "question": display_text,
                "options": []
            }
            
        # 3. TRƯỜNG HỢP NỐI DÒNG (Câu hỏi dài xuống dòng)
        elif current_q and not is_option:
            if len(current_q["options"]) == 0:
                current_q["question"] += " " + text

    # Thêm câu cuối cùng vào list
    if current_q:
        questions.append(current_q)
        
    return questions

def batch_convert():
    # Quét toàn bộ file .docx trong thư mục
    files = glob.glob("*.docx")
    if not files:
        print("Méo thấy file nào hết bro ơi!")
        return

    for file in files:
        print(f"🚀 Đang xử lý: {file}...")
        try:
            questions = parse_docx(file)
            if not questions:
                print(f"⚠️ File {file} trống rỗng hoặc lỗi format rồi.")
                continue

            # Xuất ra CSV cùng tên với file Word, ép dấu ngoặc kép toàn bộ (QUOTE_ALL)
            output_file = file.replace(".docx", ".csv")
            with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow(["Question", "A", "B", "C", "D", "Correct"])
                
                for q in questions:
                    opts = q["options"]
                    while len(opts) < 4: opts.append(("", False))
                    
                    correct_idx = 0
                    for i, (_, h) in enumerate(opts):
                        if h: correct_idx = i; break
                    
                    writer.writerow([
                        q["question"], opts[0][0], opts[1][0], opts[2][0], opts[3][0],
                        ["A", "B", "C", "D"][correct_idx]
                    ])
            print(f"✅ Xong: {output_file} ({len(questions)} câu)")
        except Exception as e:
            print(f"❌ Lỗi file {file}: {e}")

if __name__ == "__main__":
    batch_convert()