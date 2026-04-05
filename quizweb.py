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
