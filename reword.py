import re
import csv
import glob
from docx import Document

def parse_docx(file_path):
    doc = Document(file_path)
    questions = []
    current_q = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # 1. Nhận diện câu hỏi: Bắt đầu bằng số HOẶC kết thúc bằng dấu "?"
        # File của bạn có câu hỏi dạng: "Luật nào là văn bản...?"
        if re.match(r"^\d+\.", text) or text.endswith("?"):
            # Lưu câu trước đó nếu đã đủ thông tin
            if current_q and len(current_q["options"]) >= 3:
                questions.append(current_q)

            current_q = {
                "question": text,
                "options": []
            }

        # 2. Nhận diện đáp án: Nếu đã có current_q và chưa đủ 4 đáp án
        elif current_q and len(current_q["options"]) < 4:
            is_highlighted = False
            
            # Kiểm tra highlight trong từng cụm chữ (run)
            for run in para.runs:
                if run.font.highlight_color and run.text.strip():
                    is_highlighted = True
                    break
            
            # Xử lý text: loại bỏ tiền tố A. B. C. D. nếu có (phòng trường hợp text cứng)
            clean_option = re.sub(r"^[A-D]\.\s*", "", text)
            current_q["options"].append((clean_option, is_highlighted))

        # 3. Trường hợp câu hỏi dài bị ngắt dòng (nối vào câu hỏi hiện tại)
        elif current_q and len(current_q["options"]) == 0:
            current_q["question"] += " " + text

    # Thêm câu cuối cùng
    if current_q and len(current_q["options"]) >= 3:
        questions.append(current_q)

    return questions

def to_csv(questions, output_file):
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "A", "B", "C", "D", "Correct"])

        for q in questions:
            opts = q["options"]
            # Đảm bảo luôn có đủ 4 cột để không bị lệch file CSV
            while len(opts) < 4:
                opts.append(("", False))

            # Tìm đáp án đúng dựa trên highlight
            correct_index = 0
            for i, (_, h) in enumerate(opts):
                if h:
                    correct_index = i
                    break

            writer.writerow([
                q["question"],
                opts[0][0],
                opts[1][0],
                opts[2][0],
                opts[3][0],
                ["A", "B", "C", "D"][correct_index]
            ])

def batch_convert():
    files = glob.glob("*.docx")
    if not files:
        print("Empty! Không tìm thấy file .docx nào trong thư mục.")
        return

    for file in files:
        print(f"Đang xử lý: {file}...")
        questions = parse_docx(file)

        if not questions:
            print(f"❌ Không tìm thấy câu hỏi trong {file}!")
            continue

        output_file = file.replace(".docx", ".csv")
        to_csv(questions, output_file)
        print(f"✅ Xong: {output_file} ({len(questions)} câu)")

if __name__ == "__main__":
    batch_convert()