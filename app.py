import streamlit as st
from docx import Document
import io

# 1. 頁面基礎設定
st.set_page_config(
    page_title="FFM Gold Standard Processor", 
    page_icon="✈️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 自定義 CSS 美化數字顯示
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .main-header {
        font-size: 2.5rem;
        color: #0e1117;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄設計
with st.sidebar:
    st.image("https://www.lufthansa-cargo.com/theme/images/logo.svg", width=200) # 模擬品牌感
    st.title("控制面板")
    st.divider()
    st.info("💡 提示：本工具會自動過濾 COR/OSI/OCI 雜訊，並優化 ULD 格式。")
    st.success("當前版本：V3.1 (UI Optimized)")

# 4. 主頁面標題
st.markdown('<p class="main-header">✈️ FFM 電報自動清理工具</p>', unsafe_allow_html=True)
st.caption("專為 LH FFM Word 檔案設計的數據清理與統計系統")

# 5. 上傳區塊
with st.container():
    uploaded_file = st.file_uploader("📂 請上傳 FFM Word 檔案 (.docx)", type="docx", help="支援多頁長篇電報")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    is_deleting = False
    
    trigger_on = ('COR/', 'OSI/', 'OCI/')
    trigger_off = ('020-', 'ULD/', 'CONT', 'LAST')
    
    for line in raw_lines:
        if any(line.startswith(tag) for tag in trigger_on):
            is_deleting = True
            continue
        if any(line.startswith(tag) for tag in trigger_off):
            is_deleting = False
        
        if not is_deleting:
            # 執行 ULD 格式切斷邏輯
            if line.startswith('ULD/'):
                parts = line.split('/')
                if len(parts) >= 2:
                    uld_id = parts[1].split()[0]
                    line = f"ULD/{uld_id}"
            cleaned_lines.append(line)
    
    # 數據處理
    awb_set = set([l[:12] for l in cleaned_lines if l.startswith('020-')])
    uld_set = set([l for l in cleaned_lines if l.startswith('ULD/')])
    result_text = "\n".join(cleaned_lines)

    # 6. 數據統計區 (精美儀表板)
    st.write("---")
    st.subheader("📊 航班數據概覽")
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 獨立 ULD 總數", f"{len(uld_set)} 盤")
    c2.metric("📄 獨立提單總數", f"{len(awb_set)} 筆")
    c3.metric("📝 清理後總行數", f"{len(cleaned_lines)} 行")

    # 7. 功能操作區 (下載按鈕加強)
    st.write("---")
    col_dl, col_blank = st.columns([1, 2])
    with col_dl:
        st.download_button(
            label="🚀 下載清理後的 TXT 檔案",
            data=result_text,
            file_name=f"Cleaned_{uploaded_file.name.replace('.docx', '')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # 8. 預覽區塊 (標籤頁設計)
    st.write("---")
    tab1, tab2 = st.tabs(["🔍 ULD 盤號清單", "📝 檔案內容預覽"])
    
    with tab1:
        # 使用 code 區塊讓清單更好複製
        st.code("\n".join(sorted(list(uld_set))), language="text")
        
    with tab2:
        st.text_area("前 100 行內容預覽", value="\n".join(cleaned_lines[:100]), height=400)

else:
    st.warning("👈 請先上傳檔案以開始分析")
    st.image("https://img.freepik.com/free-vector/logistics-concept-illustration_114360-1557.jpg", width=400)
