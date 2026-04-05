import csv
import glob
import os

def merge_quizzes(output_file="alltest.csv"):
    # Lấy danh sách tất cả file .csv trừ file output ra (để tránh bị lặp)
    files = [f for f in glob.glob("*.csv") if f != output_file]
    
    if not files:
        print("Không tìm thấy file CSV nào để gộp!")
        return

    with open(output_file, "w", newline="", encoding="utf-8-sig") as master_f:
        writer = csv.writer(master_f)
        
        # Ghi header chuẩn cho Google Form một lần duy nhất ở đầu
        writer.writerow(["Question", "A", "B", "C", "D", "Correct"])

        for file in files:
            print(f"Đang gộp: {file}...")
            
            # Ghi một dòng phân cách để cậu biết câu hỏi thuộc file nào
            # Dòng này sẽ xuất hiện như một "Câu hỏi" tiêu đề trong Form
            writer.writerow([f"=== CHỦ ĐỀ: {file.replace('.csv', '')} ===", "-", "-", "-", "-", "-"])

            with open(file, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader) # Bỏ qua dòng header của từng file con
                
                for row in reader:
                    # Chỉ ghi nếu dòng đó có dữ liệu (tránh dòng trống)
                    if any(row):
                        writer.writerow(row)
            
            # Thêm 1 dòng trống nhẹ giữa các phần cho thoáng (tùy chọn)
            writer.writerow([])

    print(f"\n✅ Đã gộp xong {len(files)} file vào: {output_file}")

if __name__ == "__main__":
    merge_quizzes()