import streamlit as st
import pandas as pd
from io import StringIO
import time

# Conversion constants
MARLA_PER_SARSHAI = 9
KANAL_PER_MARLA = 20
KILA_PER_KANAL = 8

def convert_to_standard_units(kanal, marla):
    """Convert Kanal and Marla to total Sarshai"""
    total_sarshai = (kanal * KANAL_PER_MARLA * MARLA_PER_SARSHAI) + (marla * MARLA_PER_SARSHAI)
    return total_sarshai

def convert_from_sarshai(total_sarshai):
    """Convert total Sarshai back to Kila, Kanal, Marla, Sarshai"""
    kila = total_sarshai // (KILA_PER_KANAL * KANAL_PER_MARLA * MARLA_PER_SARSHAI)
    remainder = total_sarshai % (KILA_PER_KANAL * KANAL_PER_MARLA * MARLA_PER_SARSHAI)

    kanal = remainder // (KANAL_PER_MARLA * MARLA_PER_SARSHAI)
    remainder %= (KANAL_PER_MARLA * MARLA_PER_SARSHAI)

    marla = remainder // MARLA_PER_SARSHAI
    sarshai = remainder % MARLA_PER_SARSHAI

    return kila, kanal, marla, sarshai

def process_data(df):
    """Process the dataframe and calculate totals"""
    # Ensure numeric columns
    df['Kanal'] = pd.to_numeric(df['Kanal'], errors='coerce').fillna(0)
    df['Marla'] = pd.to_numeric(df['Marla'], errors='coerce').fillna(0)

    # Raw totals
    total_kanal = df['Kanal'].sum()
    total_marla = df['Marla'].sum()

    # Calculate total area in Sarshai
    df['Total_Sarshai'] = df.apply(lambda row: convert_to_standard_units(row['Kanal'], row['Marla']), axis=1)

    # Calculate grand total in Sarshai
    total_sarshai = df['Total_Sarshai'].sum()

    # Convert back to Kila, Kanal, Marla, Sarshai
    kila, kanal, marla, sarshai = convert_from_sarshai(total_sarshai)

    return df, total_kanal, total_marla, kila, kanal, marla, sarshai

def main():
    st.set_page_config(page_title="Jamabandi Land Area Converter", layout="wide", page_icon="🏞️")
    st.title("🏞️ Jamabandi Land Area Calculator")
    st.markdown("Convert land area data from Kanal/Marla into totals (Kila/Kanal/Marla/Sarshai).")

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ Instructions")
        st.markdown("""
        1. **Paste data** from Jamabandi.nic.in or **upload CSV**
        2. Ensure columns include **Kanal** and **Marla**
        3. Click **Process Data**
        4. **Download** results as CSV
        """)
        st.header("📊 Expected Format")
        st.code("""Khewat  Khatoni  Khasra    Type_Land  Irrigation  Kanal  Marla
594    846      0//303    प्लाट                0       19
594    846      0//492    गढडे                0       3""")

    # Input options
    input_method = st.radio("Choose input method:", ["Paste Table Data", "Upload CSV File"], horizontal=True)
    df = None

    if input_method == "Paste Table Data":
        st.subheader("📋 Paste Data")
        sample_data = """Khewat\tKhatoni\tKhasra\tType of Land\tSource of Irrigation\tKanal\tMarla
594\t846\t0//303\tप्लाट\t\t0\t19
594\t846\t0//492\tगढडे\t\t0\t3"""
        pasted_data = st.text_area("Paste your Jamabandi data here:", height=200, value=sample_data)
        if st.button("Process Data", type="primary", key="process_paste"):
            if pasted_data:
                try:
                    df = pd.read_csv(StringIO(pasted_data), sep='\t', encoding='utf-8')
                    st.success("✅ Data parsed successfully!")
                except Exception as e:
                    st.error(f"❌ Error parsing data: {e}")
            else:
                st.warning("⚠️ Please paste some data first")

    else:
        st.subheader("📤 Upload CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", help="Upload CSV file with Kanal and Marla columns")
        if uploaded_file and st.button("Process Data", type="primary", key="process_upload"):
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
                st.success("✅ File uploaded and parsed successfully!")
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")

    if df is not None:
        with st.spinner("Processing data..."):
            time.sleep(1)
            processed_df, total_kanal, total_marla, kila, kanal, marla, sarshai = process_data(df)

        tab1, tab2 = st.tabs(["📊 Data Preview", "📈 Summary"])

        with tab1:
            st.subheader("Processed Data")
            st.dataframe(processed_df, use_container_width=True)
            csv_data = processed_df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Download Processed Data (CSV)",
                data=csv_data,
                file_name="jamabandi_data.csv",
                mime="text/csv",
                use_container_width=True
            )

        with tab2:
            st.subheader("Raw Totals")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Kanal", f"{total_kanal:,}")
            with col2:
                st.metric("Total Marla", f"{total_marla:,}")

            st.subheader("Converted Totals")
            col3, col4, col5, col6 = st.columns(4)
            with col3:
                st.metric("Kila", f"{kila:,}")
            with col4:
                st.metric("Kanal", f"{kanal:,}")
            with col5:
                st.metric("Marla", f"{marla:,}")
            with col6:
                st.metric("Sarshai", f"{sarshai:,}")

            st.success(f"**Total Area:** {kila} Kila, {kanal} Kanal, {marla} Marla, {sarshai} Sarshai")

if __name__ == "__main__":
    main()
