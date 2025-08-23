import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
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
    
    # Calculate total area in Sarshai
    df['Total_Sarshai'] = df.apply(lambda row: convert_to_standard_units(row['Kanal'], row['Marla']), axis=1)
    
    # Calculate grand total
    total_sarshai = df['Total_Sarshai'].sum()
    
    # Convert back to Kila, Kanal, Marla, Sarshai
    kila, kanal, marla, sarshai = convert_from_sarshai(total_sarshai)
    
    return df, kila, kanal, marla, sarshai

def create_excel_file(df, kila, kanal, marla, sarshai):
    """Create Excel file with formatted output"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write main data
        df.to_excel(writer, sheet_name='Land Records', index=False)
        
        # Create summary sheet
        summary_data = {
            'Unit': ['Kila', 'Kanal', 'Marla', 'Sarshai'],
            'Value': [kila, kanal, marla, sarshai]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Land Records']
        
        # Add formatting
        format_currency = workbook.add_format({'num_format': '#,##0'})
        
        # Apply formatting to numeric columns
        if 'Kanal' in df.columns and 'Marla' in df.columns:
            kanal_col = df.columns.get_loc('Kanal') + 1
            marla_col = df.columns.get_loc('Marla') + 1
            worksheet.set_column(kanal_col, kanal_col, 12, format_currency)
            worksheet.set_column(marla_col, marla_col, 12, format_currency)
    
    return output.getvalue()

def main():
    st.set_page_config(page_title="Jamabandi Land Area Converter", layout="wide", page_icon="🏞️")
    st.title("🏞️ Jamabandi Land Area Calculator")
    st.markdown("Convert land area data from Kanal/Marla to Kila/Kanal/Marla/Sarshai")
    
    # Add sidebar with instructions
    with st.sidebar:
        st.header("ℹ️ Instructions")
        st.markdown("""
        1. **Paste data** from Jamabandi.nic.in or **upload CSV**
        2. Ensure columns include **Kanal** and **Marla**
        3. Click **Process Data**
        4. **Download** in your preferred format
        """)
        
        st.header("📊 Expected Format")
        st.code("""Khewat  Khatoni  Khasra    Type_Land  Irrigation  Kanal  Marla
594    846      0//303    प्लाट                0       19
594    846      0//492    गढडे                0       3""")
    
    # Input options
    input_method = st.radio("Choose input method:", 
                           ["Paste Table Data", "Upload CSV File"],
                           horizontal=True)
    
    df = None
    
    if input_method == "Paste Table Data":
        st.subheader("📋 Paste Data")
        
        # Sample data template
        sample_data = """Khewat\tKhatoni\tKhasra\tType of Land\tSource of Irrigation\tKanal\tMarla
594\t846\t0//303\tप्लाट\t\t0\t19
594\t846\t0//492\tगढडे\t\t0\t3"""
        
        with st.expander("📝 Click to copy sample format"):
            st.code(sample_data)
            if st.button("Copy Sample Format", key="copy_sample"):
                st.session_state.pasted_data = sample_data
                st.success("Sample format copied to input area!")
        
        pasted_data = st.text_area("Paste your Jamabandi data here:", 
                                  height=200,
                                  value=st.session_state.get('pasted_data', ''))
        
        if st.button("Process Data", type="primary", key="process_paste"):
            if pasted_data:
                try:
                    df = pd.read_csv(pd.compat.StringIO(pasted_data), sep='\t', encoding='utf-8')
                    st.success("✅ Data parsed successfully!")
                except Exception as e:
                    st.error(f"❌ Error parsing data: {e}")
            else:
                st.warning("⚠️ Please paste some data first")
    
    else:  # File upload
        st.subheader("📤 Upload CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file", 
                                        type="csv",
                                        help="Upload CSV file with Kanal and Marla columns")
        
        if uploaded_file and st.button("Process Data", type="primary", key="process_upload"):
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
                st.success("✅ File uploaded and parsed successfully!")
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")
    
    if df is not None:
        # Show processing animation
        with st.spinner("Processing data..."):
            time.sleep(1)  # Simulate processing time
            processed_df, kila, kanal, marla, sarshai = process_data(df)
        
        # Display results in tabs
        tab1, tab2, tab3 = st.tabs(["📊 Data Preview", "📈 Summary", "💾 Export Options"])
        
        with tab1:
            st.subheader("Processed Data")
            st.dataframe(processed_df, use_container_width=True)
        
        with tab2:
            st.subheader("Total Land Area Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Kila", f"{kila:,}", help="1 Kila = 8 Kanal")
            with col2:
                st.metric("Kanal", f"{kanal:,}", help="1 Kanal = 20 Marla")
            with col3:
                st.metric("Marla", f"{marla:,}", help="1 Marla = 9 Sarshai")
            with col4:
                st.metric("Sarshai", f"{sarshai:,}")
            
            st.success(f"**Total Area:** {kila} Kila, {kanal} Kanal, {marla} Marla, {sarshai} Sarshai")
        
        with tab3:
            st.subheader("Download Processed Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV Download
                csv_data = processed_df.to_csv(index=False, encoding='utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="jamabandi_data.csv",
                    mime="text/csv",
                    help="Download as CSV file"
                )
            
            with col2:
                # Excel Download
                excel_data = create_excel_file(processed_df, kila, kanal, marla, sarshai)
                st.download_button(
                    label="💾 Download Excel",
                    data=excel_data,
                    file_name="jamabandi_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download as Excel file with formatting"
                )
            
            st.info("💡 Choose the format that works best for your needs!")

if __name__ == "__main__":
    main()
