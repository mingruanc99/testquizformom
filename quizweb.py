import streamlit as st
import pandas as pd

# 1. Cấu hình trang
st.set_page_config(page_title="Hệ thống ôn tập 1.000 câu", page_icon="📚", layout="wide")

# 2. Hàm load và làm sạch dữ liệu
@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv("alltest.csv").dropna(subset=['Question'])
        df.columns = df.columns.str.strip().str.replace('^[^a-zA-Z0-9]+', '', regex=True)
        
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

# 3. Khởi tạo Session State
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

# --- LỌC DỮ LIỆU CHÍNH (Xử lý trước Sidebar để cập nhật giao diện đúng) ---
with st.sidebar:
    st.title("Quản lý Quiz ⚙️")
    
    # Chọn chuyên đề
    selected_topic = st.selectbox("Chọn chuyên đề ôn tập:", list(topics.keys()))
    start_range, end_range = topics[selected_topic]
    
    st.divider()
    
    # Thanh tìm kiếm
    search_query = st.text_input("🔍 Tìm kiếm câu hỏi (từ khóa):", "").strip().lower()

# Tạo dataframe để hiển thị dựa trên chuyên đề và tìm kiếm
display_df = df.iloc[start_range:end_range].copy()

if search_query:
    # str.contains giúp tìm chính xác kể cả khi cậu chỉ gõ 3 từ đầu tiên
    display_df = display_df[display_df['Question'].str.lower().str.contains(search_query, na=False)]

# Đảm bảo current_index không bị vượt quá số lượng câu hỏi sau khi lọc
max_val = max(0, len(display_df) - 1)
if st.session_state.current_index > max_val:
    st.session_state.current_index = 0

# --- TIẾP TỤC SIDEBAR SAU KHI ĐÃ CÓ DATA ĐÃ LỌC ---
with st.sidebar:
    if search_query:
        st.caption(f"🔎 Tìm thấy: {len(display_df)} câu")

    # Reset điểm và tiến độ cho phần đang hiển thị
    if st.button("Làm lại phần này"):
        st.session_state.score = 0
        st.session_state.current_index = 0
        st.session_state.answered = False
        st.rerun()

    st.divider()
    
    # Tính năng nhảy câu an toàn
    st.write("📍 Nhảy đến câu:")
    jump_index = st.number_input(f"Nhập số câu (0 - {max_val}):", 
                                 min_value=0, max_value=max_val, 
                                 value=st.session_state.current_index)
    if st.button("Đi đến"):
        st.session_state.current_index = jump_index
        st.session_state.answered = False
        st.rerun()

    st.divider()
    # Hiển thị điểm số luôn cập nhật mới nhất
    st.metric("🏆 Điểm hiện tại", st.session_state.score)


# --- GIAO DIỆN CHÍNH ---
st.title("🚀 Chế độ ôn luyện tập trung")

# Chặn lỗi nếu không có dữ liệu
if display_df.empty:
    st.warning("Không tìm thấy câu hỏi nào phù hợp với bộ lọc của bạn.")
    st.stop()

# Lấy dữ liệu câu hiện tại từ DataFrame đã lọc
row = display_df.iloc[st.session_state.current_index]

# Hiển thị Progress
total_in_topic = len(display_df)
progress_val = (st.session_state.current_index + 1) / total_in_topic
st.progress(progress_val)
st.write(f"Câu hỏi: {st.session_state.current_index + 1} / {total_in_topic}")

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
if not st.session_state.answered:
    if st.button("Kiểm tra đáp án", use_container_width=True):
        st.session_state.answered = True
        correct_ans = str(row.get('Correct', 'A')).strip().upper()
        
        if choice == correct_ans:
            st.session_state.score += 1
            
        st.rerun()

# Hiển thị kết quả
if st.session_state.answered:
    correct_ans = str(row.get('Correct', 'A')).strip().upper()
    
    if choice == correct_ans:
        st.success(f"Chính xác! Đáp án đúng là {correct_ans}")
    else:
        st.error(f"Sai rồi! Đáp án đúng phải là {correct_ans}")
    
    # Chuyển câu tiếp theo
    if st.button("Câu tiếp theo ➡️", use_container_width=True):
        if st.session_state.current_index < max_val:
            st.session_state.current_index += 1
            st.session_state.answered = False
            st.rerun()
        else:
            st.balloons()
            st.success(f"🎉 Hoàn thành phần này! Điểm của bạn: {st.session_state.score}")

st.divider()