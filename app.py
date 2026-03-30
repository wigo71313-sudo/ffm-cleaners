import streamlit as st
from docx import Document
import io

# 網頁標題與設定
st.set_page_config(page_title="FFM 電報金牌處理器", page_icon="✈️")

st.title("✈️ FFM 電報自動清理工具")
st.info("請上傳 LH FFM Word 檔案 (.docx)，系統將自動過濾 COR/OSI/OCI 雜訊。")

# 上傳元件
uploaded_file = st.file_uploader("選擇您的 FFM 檔案", type="docx")

if uploaded_file is not None:
    # 讀取 Word
    doc = Document(uploaded_file)
    full_text = [para.text for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    is_deleting = False
    trigger_on = ('COR/', 'OSI/', 'OCI/')
    trigger_off = ('020-', 'ULD/', 'CONT', 'LAST')
    
    # 核心金牌邏輯執行
    for line in full_text:
        stripped_line = line.strip()
        if any(stripped_line.startswith(tag) for tag in trigger_on):
            is_deleting = True
            continue
        if any(stripped_line.startswith(tag) for tag in trigger_off):
            is_deleting = False
        
        if not is_deleting:
            cleaned_lines.append(line)
    
    result_text = "\n".join(cleaned_lines)
    
    # 🔍 自動數據統計 (這是你要的功能)
    uld_list = [l for l in cleaned_lines if l.startswith('ULD/')]
    awb_list = [l[:12] for l in cleaned_lines if l.startswith('020-')]
    unique_awbs = set(awb_list)
    
    # 顯示結果儀表板
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ULD 裝備總數", len(uld_list))
    with col2:
        st.metric("獨立提單筆數", len(unique_awbs))
    
    # 下載按鈕
    st.download_button(
        label="📥 下載清理後的 TXT 檔案",
        data=result_text,
        file_name="Cleaned_FFM_Result.txt",
        mime="text/plain"
    )
    
    # 預覽功能
    with st.expander("查看清理後的前 500 字內容"):
        st.text(result_text[:1000])
