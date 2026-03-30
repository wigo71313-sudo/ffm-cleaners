import streamlit as st
from docx import Document
import io

# 網頁標題與分頁設定
st.set_page_config(page_title="FFM 金牌處理器 V2.1", page_icon="✈️", layout="wide")

st.title("✈️ FFM 電報自動清理與數據分析")
st.info("支援長篇電報（如 72 頁文件），自動過濾雜訊並精確統計裝備與提單。")

# 側邊欄：顯示邏輯說明
with st.sidebar:
    st.header("🛠️ 處理邏輯")
    st.write("1. **開關制過濾**：自動剔除 COR/OSI/OCI 及其下方描述。")
    st.write("2. **精準計數**：自動剔除跨頁重複的 ULD 與 AWB。")
    st.write("3. **格式優化**：ULD 清單僅保留『編號』，去除重量與體積雜訊。")

# 上傳元件
uploaded_file = st.file_uploader("請上傳 FFM Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    # 讀取 Word 檔案內容
    doc = Document(uploaded_file)
    # 讀取所有段落並過濾掉純空行
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    is_deleting = False
    
    # 定義觸發標籤
    trigger_on = ('COR/', 'OSI/', 'OCI/')
    trigger_off = ('020-', 'ULD/', 'CONT', 'LAST')
    
    # 執行金牌過濾邏輯
    for line in raw_lines:
        if any(line.startswith(tag) for tag in trigger_on):
            is_deleting = True
            continue
        if any(line.startswith(tag) for tag in trigger_off):
            is_deleting = False
        
        if not is_deleting:
            cleaned_lines.append(line)
    
    # --- 數據精準統計與格式化區 ---
    # 1. 提取所有 ULD 編號並優化格式 (僅保留 ULD/XXXXXXXXXX)
    uld_clean_list = []
    for l in cleaned_lines:
        if l.startswith('ULD/'):
            # 透過斜線與空格切割，只抓取盤號主體
            parts = l.split('/')
            if len(parts) >= 2:
                # 取得盤號並去除後方所有資訊 (如 W-1550...)
                uld_id = parts[1].split()[0] 
                uld_clean_list.append(f"ULD/{uld_id}")
    
    uld_set = set(uld_clean_list) # 執行去重
    
    # 2. 提取所有提單號碼 (前 12 碼) 並去重
    awb_set = set([l[:12] for l in cleaned_lines if l.startswith('020-')])
    
    # 顯示數據儀表板
    st.subheader("📊 數據統計結果")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("獨立 ULD 裝備總數", len(uld_set))
    with col2:
        st.metric("獨立主提單筆數", len(awb_set))
    with col3:
        st.metric("清理後總行數", len(cleaned_lines))

    # 下載區
    result_text = "\n".join(cleaned_lines)
    st.divider()
    st.download_button(
        label="📥 下載清理後的 TXT 檔案",
        data=result_text,
        file_name="Cleaned_FFM_Result.txt",
        mime="text/plain",
        use_container_width=True
    )

    # 預覽詳細內容
    with st.expander("🔍 檢視獨立 ULD 清單 (已簡化格式)"):
        # 排序後顯示，方便核對
        st.write(sorted(list(uld_set)))
        
    with st.expander("🔍 檢視清理後的文字預覽"):
        st.text(result_text[:2000] + "\n\n...(下方省略)")
