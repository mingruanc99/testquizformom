import streamlit as st
import pandas as pd
import random

# Thiết lập giao diện trang
st.set_page_config(page_title="My Interactive Quiz", page_icon="📚")

# Load dữ liệu từ file CSV đã gộp của cậu
@st.cache_data
def load_data():
    # Đọc file CSV (đảm bảo file có các cột: Question, A, B, C, D, Correct)
    df = pd.read_csv("alltest.csv")
    return df

df = load_data()

# Khởi tạo trạng thái phiên (Session State)
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

# Sidebar điều hướng
st.sidebar.title("Quản lý Quiz")
st.sidebar.write(f"Tổng số câu: {len(df)}")
st.sidebar.progress((st.session_state.current_index + 1) / len(df))

# Hiển thị câu hỏi hiện tại
row = df.iloc[st.session_state.current_index]

st.title(f"Câu hỏi {st.session_state.current_index + 1}")
st.subheader(row['Question'])

# Hiển thị các lựa chọn ABCD
options = {
    "A": row['A'],
    "B": row['B'],
    "C": row['C'],
    "D": row['D']
}

# Radio button để chọn đáp án
choice = st.radio("Chọn đáp án của bạn:", list(options.keys()), 
                  format_func=lambda x: f"{x}. {options[x]}",
                  key=f"q_{st.session_state.current_index}",
                  disabled=st.session_state.answered)

# Nút kiểm tra
if st.button("Kiểm tra đáp án") and not st.session_state.answered:
    st.session_state.answered = True
    correct_ans = str(row['Correct']).strip().upper()
    
    if choice == correct_ans:
        st.success(f"Chính xác! Đáp án là {correct_ans}")
        st.session_state.score += 1
    else:
        st.error(f"Sai rồi! Đáp án đúng phải là {correct_ans}")

# Nút chuyển câu tiếp theo
if st.session_state.answered:
    if st.button("Câu tiếp theo ➡️"):
        if st.session_state.current_index < len(df) - 1:
            st.session_state.current_index += 1
            st.session_state.answered = False
            st.rerun()
        else:
            st.balloons()
            st.write(f"🎉 Chúc mừng! Bạn đã hoàn thành bộ quiz với số điểm {st.session_state.score}/{len(df)}")

# Hiển thị điểm số hiện tại ở cuối trang
st.divider()
st.write(f"Điểm hiện tại: {st.session_state.score}")