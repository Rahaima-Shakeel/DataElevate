import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set page configuration
st.set_page_config(page_title="Data Elevate 🚀", layout="wide")
st.markdown("<h1 style='text-align: center;'>Data Elevate ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Transform your files between CSV and Excel formats with built-in data cleaning, visualization, and analysis!</p>", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose a mode:", ["Upload & Process Files", "About"])

if app_mode == "About":
    st.sidebar.info("This app allows you to upload CSV or Excel files, clean data, visualize, and convert formats. Enjoy a streamlined data processing experience!")
    st.stop()

# File uploader widget in the main page
uploaded_files = st.file_uploader("Upload your files (CSV or Excel): 📁", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    # Loop through each uploaded file
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read the file based on extension
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file_ext} ❌")
                continue
        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")
            continue

        # File information
        st.markdown(f"### {file.name} 📝")
        st.markdown(f"**File Size:** {file.size / 1024:.2f} KB 📏")
        st.markdown("**Data Preview:**")
        st.dataframe(df.head())

        # Data Summary & Statistics
        st.subheader("Data Summary 📊")
        st.write("**Basic Statistics:**")
        st.write(df.describe(include="all").T)
        st.write("**Missing Values Count:**")
        st.write(df.isnull().sum())

        # Data Cleaning Options
        st.subheader("Data Cleaning Options 🧼")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    before_count = len(df)
                    df.drop_duplicates(inplace=True)
                    after_count = len(df)
                    st.success(f"Removed {before_count - after_count} duplicate rows! ✅")
            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("Missing numeric values filled with column means! 💧")
        
        # Column selection for processing
        st.subheader("Select Columns to Process 📋")
        selected_columns = st.multiselect(f"Choose columns for {file.name}", df.columns.tolist(), default=df.columns.tolist())
        if selected_columns:
            df = df[selected_columns]

        # Data Visualization Options
        st.subheader("Data Visualization Options 📈")
        if st.checkbox(f"Show Visualization for {file.name}"):
            # Let user choose the chart type
            chart_type = st.selectbox("Select chart type:", ["Bar Chart", "Line Chart", "Area Chart", "Scatter Plot"])
            numeric_df = df.select_dtypes(include=["number"])
            if numeric_df.empty:
                st.warning("No numeric data available for visualization.")
            else:
                if chart_type == "Bar Chart":
                    st.bar_chart(numeric_df)
                elif chart_type == "Line Chart":
                    st.line_chart(numeric_df)
                elif chart_type == "Area Chart":
                    st.area_chart(numeric_df)
                elif chart_type == "Scatter Plot":
                    # For scatter plot, allow selection of two numeric columns
                    cols = numeric_df.columns.tolist()
                    if len(cols) >= 2:
                        x_axis = st.selectbox("X-Axis", cols, key=f"x_{file.name}")
                        y_axis = st.selectbox("Y-Axis", cols, key=f"y_{file.name}")
                        st.write("Scatter Plot:")
                        st.altair_chart(
                            pd.concat([numeric_df[x_axis], numeric_df[y_axis]], axis=1)
                            .reset_index()
                            .pipe(lambda d: st._legacy_altair_chart(
                                alt.Chart(d).mark_circle(size=60).encode(x=x_axis, y=y_axis, tooltip=["index", x_axis, y_axis]).interactive()
                            )),
                            use_container_width=True
                        )
                    else:
                        st.warning("Need at least 2 numeric columns for scatter plot.")
        
        # File conversion options
        st.subheader("Conversion Options 🔄")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                new_file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False)
                new_file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            st.download_button(
                label=f"Download {new_file_name} as {conversion_type} 📥",
                data=buffer,
                file_name=new_file_name,
                mime=mime_type
            )
    st.success("All Files Processed! 🎉")
else:
    st.info("Please upload one or more CSV or Excel files to get started.")