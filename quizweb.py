import streamlit as st
import pandas as pd

# 1. Thiết lập trang
st.set_page_config(page_title="Quiz Bất Động Sản Pro", page_icon="⚡", layout="wide")

# 2. Hàm load dữ liệu "sạch"
@st.cache_data
def get_data():
    try:
        # Đọc file và loại bỏ các dòng không có câu hỏi
        df = pd.read_csv("alltest.csv").dropna(subset=['Question'])
        # Làm sạch tên cột để tránh lỗi KeyError
        df.columns = df.columns.str.strip().str.replace('^[^a-zA-Z0-9]+', '', regex=True)
        
        topic_rows = df[df['Question'].str.contains('===', na=False)].index.tolist()
        topics = {}
        last_idx = 0
        current_label = "Chung"
        
        for idx in topic_rows:
            label = df.iloc[idx]['Question'].replace('=', '').strip()
            topics[current_label] = (last_idx, idx)
            current_label = label
            last_idx = idx + 1
        
        topics[current_label] = (last_idx, len(df))
        return df, topics
    except Exception as e:
        st.error(f"Lỗi load file: {e}")
        return pd.DataFrame(), {}

df, topics = get_data()

# 3. Kiểm tra dữ liệu đầu vào
if df.empty:
    st.error("Không tìm thấy dữ liệu trong file alltest.csv!")
    st.stop()

# 4. Quản lý Session State
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings ⚙️")
    selected_topic = st.selectbox("Chọn chuyên đề:", list(topics.keys()))
    start_range, end_range = topics[selected_topic]
    
    if st.button("Làm lại chuyên đề này"):
        st.session_state.current_index = start_range
        st.session_state.score = 0
        st.rerun()

    st.divider()
    jump_index = st.number_input("📍 Nhảy đến câu số:", min_value=0, max_value=len(df)-1, value=st.session_state.current_index)
    if st.button("Đi ngay"):
        st.session_state.current_index = jump_index
        st.session_state.answered = False
        st.rerun()

# --- GIAO DIỆN CHÍNH ---
st.title("📚 Ôn tập 1.000 câu - Lưu tiến độ")

# Đảm bảo index luôn nằm trong chuyên đề đã chọn
if not (start_range <= st.session_state.current_index < end_range):
    st.session_state.current_index = start_range

total_in_topic = end_range - start_range

# 🛡️ ĐIỂM CHẶN LỖI TỐI QUAN TRỌNG
if total_in_topic <= 0:
    st.warning(f"Chuyên đề '{selected_topic}' đang trống!")
    st.stop() # Dừng app tại đây để không bị lỗi NameError bên dưới

# Lấy dữ liệu câu hỏi hiện tại
row = df.iloc[st.session_state.current_index]

# Hiển thị tiến độ
progress = (st.session_state.current_index - start_range + 1) / total_in_topic
st.progress(progress)
st.write(f"Tiến độ: {st.session_state.current_index - start_range + 1} / {total_in_topic} | Tổng điểm: {st.session_state.score}")

# Hiển thị nội dung Quiz
st.markdown(f"### {row['Question']}")

# Lấy đáp án an toàn (phòng trường hợp file CSV thiếu cột)
opts_dict = {
    "A": row.get('A', 'N/A'),
    "B": row.get('B', 'N/A'),
    "C": row.get('C', 'N/A'),
    "D": row.get('D', 'N/A')
}

choice = st.radio(
    "Chọn đáp án:", 
    list(opts_dict.keys()), 
    format_func=lambda x: f"{x}. {opts_dict[x]}",
    key=f"radio_{st.session_state.current_index}",
    disabled=st.session_state.answered
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Nộp bài ✅", use_container_width=True) and not st.session_state.answered:
        st.session_state.answered = True
        correct_ans = str(row.get('Correct', 'A')).strip().upper()
        if choice == correct_ans:
            st.success("Chính xác!")
            st.session_state.score += 1
        else:
            st.error(f"Sai rồi! Đáp án đúng là {correct_ans}")
        st.rerun()

with col2:
    if st.session_state.answered:
        if st.button("Câu tiếp theo ➡️", use_container_width=True):
            if st.session_state.current_index < end_range - 1:
                st.session_state.current_index += 1
                st.session_state.answered = False
                st.rerun()
            else:
                st.balloons()
                st.success("Hoàn thành chuyên đề!")
