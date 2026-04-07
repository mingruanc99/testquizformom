import streamlit as st
import pandas as pd

# 1. Cấu hình trang
st.set_page_config(page_title="Hệ thống ôn tập 1.000 câu", page_icon="📚", layout="wide")

# 2. Hàm load và làm sạch dữ liệu
@st.cache_data
def load_and_clean_data():
    try:
        # Đọc file CSV của cậu
        df = pd.read_csv("alltest.csv").dropna(subset=['Question'])
        # Xóa khoảng trắng thừa và ký tự lạ ở tên cột
        df.columns = df.columns.str.strip().str.replace('^[^a-zA-Z0-9]+', '', regex=True)
        
        # Phân tách chuyên đề dựa trên dấu ===
        topic_rows = df[df['Question'].str.contains('===', na=False)].index.tolist()
        topics = {}
        last_idx = 0
        current_label = "Tổng hợp"
        
        for idx in topic_rows:
            label = df.iloc[idx]['Question'].replace('=', '').strip()
            topics[current_label] = (last_idx, idx)
            current_label = label
            last_idx = idx + 1
        
        topics[current_label] = (last_idx, len(df))
        return df, topics
    except Exception as e:
        st.error(f"Không tìm thấy hoặc lỗi file alltest.csv: {e}")
        return pd.DataFrame(), {}

df, topics = load_and_clean_data()

# 3. Khởi tạo Session State (Quan trọng để chấm điểm và lưu tiến độ)
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

# --- SIDEBAR: QUẢN LÝ ---
with st.sidebar:
    st.title("Quản lý Quiz ⚙️")
    
    # 1. Chọn chuyên đề
    selected_topic = st.selectbox("Chọn chuyên đề ôn tập:", list(topics.keys()))
    start_range, end_range = topics[selected_topic]
    
    # 2. Thanh Tìm kiếm (Search Engine thu nhỏ cho 1.000 câu)
    st.divider()
    search_query = st.text_input("🔍 Tìm kiếm câu hỏi (từ khóa):", "").strip().lower()
    
    # Logic lọc dữ liệu dựa trên Search (Phải chạy trước khi hiện Điểm và Nhảy câu)
    display_df = df.iloc[start_range:end_range].copy()
    if search_query:
        display_df = display_df[display_df['Question'].str.lower().str.contains(search_query, na=False)]

    # 3. Nút Reset (Lưu ý: Reset cả trạng thái Answered)
    if st.button("Làm lại chuyên đề này"):
        st.session_state.score = 0
        st.session_state.current_index = 0 # Reset về câu đầu tiên của kết quả lọc
        st.session_state.answered = False
        st.rerun()

    st.divider()
    
    # 4. Tính năng nhảy câu (Max value phải dựa trên display_df để tránh IndexError)
    st.write("📍 Nhảy đến câu:")
    max_val = max(0, len(display_df) - 1)
    jump_index = st.number_input(f"Nhập số câu (0 - {max_val}):", 
                                 min_value=0, max_value=max_val, 
                                 value=min(st.session_state.current_index, max_val))
    
    if st.button("Đi đến"):
        st.session_state.current_index = jump_index
        st.session_state.answered = False
        st.rerun()

    st.divider()
    
    # 5. HIỂN THỊ ĐIỂM (Cập nhật Real-time)
    # Dùng st.metric nhìn cho chuyên nghiệp giống mấy con app AI cậu đang học
    st.metric(label="🏆 Điểm số hiện tại", value=st.session_state.score)
    
    if search_query:
        st.caption(f"🔎 Đang lọc được: {len(display_df)} câu")

# --- GIAO DIỆN CHÍNH ---
st.title("🚀 Chế độ ôn luyện tập trung")

# Đảm bảo index nằm trong chuyên đề
if not (start_range <= st.session_state.current_index < end_range):
    st.session_state.current_index = start_range

total_in_topic = end_range - start_range

# Chặn lỗi nếu chuyên đề trống
if total_in_topic <= 0:
    st.warning(f"Chuyên đề '{selected_topic}' không có câu hỏi.")
    st.stop()

# Lấy dữ liệu câu hiện tại
row = df.iloc[st.session_state.current_index]

# Hiển thị Progress
progress_val = (st.session_state.current_index - start_range + 1) / total_in_topic
st.progress(progress_val)
st.write(f"Câu hỏi: {st.session_state.current_index - start_range + 1} / {total_in_topic}")

# Nội dung câu hỏi
st.subheader(row['Question'])

# Lựa chọn đáp án
options = {
    "A": row.get('A', 'Trống'),
    "B": row.get('B', 'Trống'),
    "C": row.get('C', 'Trống'),
    "D": row.get('D', 'Trống')
}

choice = st.radio("Chọn đáp án của bạn:", list(options.keys()), 
                  format_func=lambda x: f"{x}. {options[x]}",
                  key=f"q_{st.session_state.current_index}",
                  disabled=st.session_state.answered)

# --- LOGIC KIỂM TRA & HIỂN THỊ THÔNG BÁO ---
# Nút kiểm tra chỉ hiện khi chưa trả lời
if not st.session_state.answered:
    if st.button("Kiểm tra đáp án", use_container_width=True):
        st.session_state.answered = True
        # Lấy đáp án đúng từ file CSV
        correct_ans = str(row.get('Correct', 'A')).strip().upper()
        
        # Kiểm tra và cộng điểm
        if choice == correct_ans:
            st.session_state.last_result = "success"
        else:
            st.session_state.last_result = "error"
            st.session_state.correct_val = correct_ans # Lưu lại để hiện thông báo
        
        if st.session_state.last_result == "success":
            st.session_state.score += 1
        st.rerun()

# Hiển thị thông báo sau khi đã bấm nút (Dòng này giúp thông báo giữ nguyên)
if st.session_state.answered:
    correct_ans = str(row.get('Correct', 'A')).strip().upper()
    
    if choice == correct_ans:
        st.success(f"Chính xác! Đáp án đúng là {correct_ans}")
    else:
        # ĐÂY CHÍNH LÀ PHẦN CẬU MUỐN (Giống ảnh 100%)
        st.error(f"Sai rồi! Đáp án đúng phải là {correct_ans}")
    
    # Hiện nút chuyển câu tiếp theo
    if st.button("Câu tiếp theo ➡️", use_container_width=True):
        if st.session_state.current_index < end_range - 1:
            st.session_state.current_index += 1
            st.session_state.answered = False
            st.rerun()
        else:
            st.balloons()
            st.success(f"🎉 Hoàn thành! Điểm của bạn: {st.session_state.score}")

# Lọc dữ liệu - Chức năng tìm kiếm
display_df = df.iloc[start_range:end_range].copy()

# Nếu có từ khóa tìm kiếm, lọc tiếp trên display_df
if search_query:
    display_df = display_df[display_df['Question'].str.lower().str.contains(search_query, na=False)]
    if display_df.empty:
        st.warning(f"Không tìm thấy câu hỏi nào chứa từ khóa: '{search_query}'")
        st.stop()

# Đảm bảo index không vượt quá số lượng câu sau khi lọc
max_idx = len(display_df) - 1
if st.session_state.current_index > max_idx:
    st.session_state.current_index = 0

# Lấy câu hỏi hiện tại từ dataframe đã lọc
row = display_df.iloc[st.session_state.current_index]
st.write(f"Tìm thấy {len(display_df)} câu hỏi phù hợp.")
progress_val = (st.session_state.current_index + 1) / len(display_df)
st.progress(progress_val)


st.divider()
st.write(f"Tiến độ tổng thể: {st.session_state.current_index + 1} / {len(df)}")