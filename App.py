# To run the app use the command streamlit run app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from nlp_manager import NLPManager
from config import UI_CONFIG

# --- App Config ---
st.set_page_config(page_title="Data Explorer with Natural Commands", layout="wide")

st.title(" Data Explorer with Natural Commands")

# --- Session State ---
if "nlp" not in st.session_state:
    st.session_state["nlp"] = NLPManager()
if "df" not in st.session_state:
    st.session_state["df"] = None
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None

nlp = st.session_state["nlp"]

# --- File Uploader ---
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state["df"] = df
    nlp.set_dataset(df)
    st.success(f" Loaded dataset with shape {df.shape}")

# --- Preview ---
if st.session_state["df"] is not None:
    with st.expander(" Data Preview"):
        st.dataframe(st.session_state["df"].head(UI_CONFIG["default_preview_rows"]))

    # --- NL Command Box ---
    st.subheader(" Ask your data a question")
    query = st.text_input("Enter a natural language command", placeholder="e.g., show seasonality by region")

    if st.button("Run"):
        if query.strip():
            result = nlp.process_query(query)
            st.session_state["last_result"] = result
        else:
            st.warning("Please enter a query first.")

    # --- Suggestions Panel ---
    if st.session_state["last_result"]:
        result = st.session_state["last_result"]

        if "error" in result:
            st.error(result["error"])
        else:
            st.markdown(f"**Query:** {result['query']}")
            st.markdown(f"**Message:** {result['message']}")

            # Suggestions
            st.subheader(" Suggestions")
            for i, sug in enumerate(result["suggestions"], 1):
                if st.button(f"Apply Suggestion {i}: {sug['explanation']}"):
                    # Re-execute selected suggestion
                    parsed = sug["parsed"]
                    sug_result = nlp._execute_operation(parsed)
                    nlp.current_view = sug_result
                    st.session_state["last_result"]["result_data"] = sug_result
                    st.session_state["last_result"]["primary"] = sug

            # Operation Explanation
            if "primary" in result:
                st.info(f" {result['primary']['explanation']}")

            # Chart/Table
            if result["result_data"] is not None:
                df_result = result["result_data"]

                st.subheader(" Visualization")
                try:
                    # Try plotting if numeric data
                    numeric_cols = df_result.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) >= 1:
                        fig = px.bar(df_result, x=df_result.columns[0], y=numeric_cols[0], height=UI_CONFIG["chart_height"])
                        st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

                st.subheader("📋 Data Output")
                st.dataframe(df_result)

                # --- Export Options ---
                st.subheader(" Export")
                fmt = st.selectbox("Select format", UI_CONFIG["export_formats"])
                if st.button("Download"):
                    export_data = nlp.get_export_data(fmt)
                    if export_data:
                        st.download_button(
                            label=f"Download as {fmt.upper()}",
                            data=export_data,
                            file_name=f"export.{fmt}",
                            mime="text/csv" if fmt == "csv" else "application/json"
                        )
                    else:
                        st.warning("No data available to export.")
