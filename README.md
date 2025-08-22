# 🏞️ Jamabandi Land Area Converter

A Streamlit web application that processes land area data from Jamabandi.nic.in and converts between traditional North Indian land measurement units (Kila, Kanal, Marla, Sarshai).

## ✨ Features

- **Multiple Input Methods**: Paste data directly or upload CSV files
- **Unit Conversion**: Automatically converts Kanal+Marla to Kila/Kanal/Marla/Sarshai
- **Multiple Export Formats**: Download results as CSV, Excel, or Word documents
- **User-Friendly Interface**: Intuitive design with clear instructions
- **Real-time Processing**: Instant calculations with visual feedback

## 📋 Expected Input Data Format

The application expects tabular data with the following columns (order matters):

### Required Columns:
- **Khewat**: Land record number
- **Khatoni**: Sub-record number  
- **Khasra**: Plot number (e.g., `0//303`, `114//11`)
- **Type of Land**: Land type in Hindi (e.g., `प्लाट`, `नहरी`, `चाही`)
- **Source of Irrigation**: Irrigation source (can be empty)
- **Kanal**: Area in Kanal (numeric)
- **Marla**: Area in Marla (numeric)

### Example Input Format:
