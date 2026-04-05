import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(page_title="Quiz Bất động sản", page_icon="⚡", layout="wide")

# 1. Load dữ liệu và phân tách chuyên đề
@st.cache_data
@st.cache_data
def get_data():
    # Đọc file và loại bỏ các dòng hoàn toàn trống
    df = pd.read_csv("merged_all_quizzes.csv").dropna(how='all')
    
    # 🛡️ SỬA LỖI TẠI ĐÂY: Làm sạch tên cột (xóa khoảng trắng, ký tự ẩn)
    df.columns = df.columns.str.strip().str.replace('^[^a-zA-Z0-9]+', '', regex=True)
    
    # Kiểm tra xem có cột 'Question' không, nếu không có thì báo lỗi trực quan
    if 'Question' not in df.columns:
        st.error(f"Không tìm thấy cột 'Question'. Các cột hiện có: {list(df.columns)}")
        st.stop()

    # Tìm vị trí các dòng tiêu đề chuyên đề
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

df, topics = get_data()

# 2. Quản lý Session State (Lưu tiến độ)
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

# --- SIDEBAR: ĐIỀU HƯỚNG & LƯU QUÁ TRÌNH ---
with st.sidebar:
    st.title("Settings ⚙️")
    
    # Chọn chuyên đề
    selected_topic = st.selectbox("Chọn chuyên đề ôn tập:", list(topics.keys()))
    start_range, end_range = topics[selected_topic]
    
    # Nút Reset điểm
    if st.button("Làm lại từ đầu (Reset Score)"):
        st.session_state.score = 0
        st.session_state.current_index = start_range
        st.rerun()

    st.divider()
    
    # "Lưu quá trình" bằng cách nhảy đến số câu cụ thể
    st.write("📍 Lưu tiến độ:")
    jump_index = st.number_input(
        f"Nhảy đến câu (0 - {len(df)-1}):", 
        min_value=0, 
        max_value=len(df)-1, 
        value=st.session_state.current_index
    )
    if st.button("Đi đến câu này"):
        st.session_state.current_index = jump_index
        st.session_state.answered = False
        st.rerun()

    st.divider()
    st.info(f"Tổng điểm: {st.session_state.score}")

# --- GIAO DIỆN CHÍNH ---
st.title("📚 Hệ thống ôn tập 1.000 câu")

# Kiểm tra nếu index hiện tại nằm ngoài range của chuyên đề đã chọn thì reset về đầu chuyên đề đó
if not (start_range <= st.session_state.current_index < end_range):
    st.session_state.current_index = start_range

# Hiển thị Progress Bar
total_in_topic = end_range - start_range
if total_in_topic > 0:
    progress = (st.session_state.current_index - start_range + 1) / total_in_topic
    st.progress(progress)
    st.write(f"Câu hỏi {st.session_state.current_index - start_range + 1} / {total_in_topic} (Trong mục: {selected_topic})")
    
    # Chỉ hiển thị câu hỏi nếu có dữ liệu
    row = df.iloc[st.session_state.current_index]
    # ... (tiếp tục phần hiển thị câu hỏi bên dưới)
else:
    st.warning(f"Chuyên đề '{selected_topic}' hiện đang trống. Cậu kiểm tra lại file CSV nhé!")

# Hiển thị câu hỏi
st.markdown(f"### {row['Question']}")

# Hiển thị đáp án
options = {"A": row['A'], "B": row['B'], "C": row['C'], "D": row['D']}
choice = st.radio(
    "Chọn đáp án:", 
    list(options.keys()), 
    format_func=lambda x: f"{x}. {options[x]}",
    key=f"radio_{st.session_state.current_index}",
    disabled=st.session_state.answered
)

# Logic kiểm tra
col1, col2 = st.columns(2)
with col1:
    if st.button("Nộp bài", use_container_width=True) and not st.session_state.answered:
        st.session_state.answered = True
        correct_ans = str(row['Correct']).strip().upper()
        
        if choice == correct_ans:
            st.success(f"Đúng rồi! +1 điểm")
            st.session_state.score += 1
        else:
            st.error(f"Sai rồi! Đáp án đúng là: {correct_ans}")
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
                st.success("Bạn đã hoàn thành chuyên đề này!")
