import streamlit as st
import pandas as pd
from docx import Document

# --- Configuration ---
WORK_ORDER_IDS = ['273496284', '279323105', '273396632']
DOCX_PATH       = 'DemoWorkOrders.docx'
SUBSET_PATH     = 'subset_data.csv'

# --- Helpers ---
@st.cache_data
def load_subset():
    return pd.read_csv(SUBSET_PATH)

@st.cache_data
def load_narratives(doc_path):
    doc = Document(doc_path)
    narratives = {}
    for para in doc.paragraphs:
        text = para.text.strip()
        for wo in WORK_ORDER_IDS:
            if text.startswith(f"{wo}:"):
                narratives[wo] = text.split(":", 1)[1].strip()
    return narratives

# --- Streamlit UI ---
st.set_page_config(page_title="Failure Prediction Demo", layout="wide")
st.title("Step 1: Failure Prediction Report")

# 1) Pre-load subset_data (for Step 2)
subset_df = load_subset()

# 2) File uploader (decorative for now)
uploaded = st.file_uploader(
    "Upload your broken_pumps_with_metadata.csv (not used yet):",
    type=['csv']
)
if uploaded is not None:
    st.markdown("**Uploaded file preview:**")
    # replace single pd.read_csv call with this block:
    try:
        df_uploaded = pd.read_csv(uploaded)
    except UnicodeDecodeError:
        uploaded.seek(0)
        df_uploaded = pd.read_csv(uploaded, encoding='latin-1')
    st.dataframe(df_uploaded.head(), use_container_width=True)

# 3) Run the “prediction” (hard-coded IDs + narratives)
if st.button("Run Failure Prediction Report"):
    narr = load_narratives(DOCX_PATH)
    st.markdown("---")
    st.markdown("## Failure Prediction Report")
    for wo in WORK_ORDER_IDS:
        text = narr.get(wo, "_No narrative found in document._")
        st.markdown(f"**WorkOrderID {wo}**")
        st.markdown(f"> {text}")
        st.markdown("")
        
# 4) Deep‐dive graphs
st.markdown("---")
st.header("Step 2: Failure Deep Dives")

if st.button("Show Failure Deep Dives"):
    for wo in WORK_ORDER_IDS:
        wo_int = int(wo)
        df_wo = subset_df[subset_df['WorkOrderID'] == wo_int]
        if df_wo.empty:
            st.write("No data found for this WorkOrderID.")
            continue

        # group by sensor name & ID
        for (sensor_name, sensor_id), grp in df_wo.groupby(['sensor_name','sensor_id']):
            grp = grp.sort_values('datetime')  # assuming your time‐column is named "datetime"
            # plot the reading vs timestamp
            st.markdown(f"**{sensor_name}** (sensor_id {sensor_id})")
            st.line_chart(
                data=grp.set_index('datetime')['reading'],
                use_container_width=True
            )
            st.markdown("")  # small spacer
