import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import json
from nlp_manager import NLPManager, ParsedQuery  # make sure ParsedQuery is imported
from config import UI_CONFIG, DATA_PATH, EXPORTS_PATH

# --- App Config ---
st.set_page_config(page_title="Data Explorer with Natural Commands", layout="wide")
st.title("Data Explorer with Natural Commands")

# --- Session State ---
if "nlp" not in st.session_state:
    st.session_state["nlp"] = NLPManager()
if "df" not in st.session_state:
    st.session_state["df"] = None
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "operations_history" not in st.session_state:
    st.session_state["operations_history"] = []

nlp = st.session_state["nlp"]

# --- File Uploader ---
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=['date'], low_memory=False)
        # Validate numeric columns
        numeric_cols = ['units_sold', 'unit_price', 'discount_pct', 'gross_revenue', 
                        'cogs', 'tax_pct', 'tax_amount', 'returned_units', 'net_revenue']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        st.session_state["df"] = df
        nlp.set_dataset(df)
        st.success(f"Loaded dataset with shape {df.shape}")
        with open(DATA_PATH / uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")

# --- Preview ---
if st.session_state["df"] is not None:
    with st.expander("Data Preview"):
        st.dataframe(st.session_state["df"].head(UI_CONFIG["default_preview_rows"]))

    # --- NL Command Box ---
    st.subheader("Ask your data a question")
    query = st.text_input("Enter a natural language command", placeholder="e.g., show seasonality by region")
    if st.button("Run"):
        if query.strip():
            result = nlp.process_query(query)
            st.session_state["last_result"] = result
            if "primary" in result and result["result_data"] is not None:
                st.session_state["operations_history"].append({
                    "query": query,
                    "operation": result["primary"],
                    "timestamp": pd.Timestamp.now().isoformat()
                })
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
            st.subheader("Suggestions")
            for i, sug in enumerate(result.get("suggestions", []), 1):
                if st.button(f"Apply Suggestion {i}: {sug['description']}"):
                    # Construct ParsedQuery from suggestion dict
                    parsed_query = ParsedQuery(
                        operation=sug.get("operation"),
                        args=sug.get("args", {}),
                        explanation=sug.get("explanation", ""),
                        confidence=sug.get("confidence", 0.8),
                        source=sug.get("source", "alternative")
                    )
                    sug_result = nlp._execute_operation(parsed_query)
                    nlp.current_view = sug_result
                    st.session_state["last_result"]["result_data"] = sug_result
                    st.session_state["last_result"]["primary"] = {
                        "operation": parsed_query.operation,
                        "args": parsed_query.args,
                        "explanation": parsed_query.explanation
                    }
                    st.session_state["operations_history"].append({
                        "query": f"Suggestion {i}: {sug['description']}",
                        "operation": parsed_query.operation,
                        "timestamp": pd.Timestamp.now().isoformat()
                    })

            # Operation Explanation
            if "primary" in result:
                st.info(f"{result['primary'].get('explanation','')}")

            # Chart/Table
            if result["result_data"] is not None:
                df_result = result["result_data"]
                st.subheader("Visualization")
                try:
                    numeric_cols = df_result.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) >= 1:
                        if result["primary"]["operation"] == "pivot_data":
                            index_col = df_result.columns[0]
                            heatmap_cols = [col for col in numeric_cols if col != index_col]
                            if heatmap_cols:
                                fig = px.imshow(df_result.set_index(index_col)[heatmap_cols], 
                                                title="Pivot Table Heatmap", 
                                                height=UI_CONFIG["chart_height"])
                            else:
                                st.warning("No numeric columns available for heatmap")
                                fig = None
                        elif "seasonality" in result["query"].lower():
                            fig = px.line(df_result, x=df_result.columns[0], y=numeric_cols[0], 
                                         title="Seasonality Trend", 
                                         height=UI_CONFIG["chart_height"])
                        else:
                            fig = px.bar(df_result, x=df_result.columns[0], y=numeric_cols[0], 
                                         title="Data Summary", 
                                         height=UI_CONFIG["chart_height"])
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No numeric columns available for visualization")
                except Exception as e:
                    st.warning(f"Could not render chart: {str(e)}")
                st.subheader("📋 Data Output")
                st.dataframe(df_result)

                # --- Export Options ---
                st.subheader("Export")
                fmt = st.selectbox("Select format", UI_CONFIG["export_formats"])
                if st.button("Download"):
                    export_data = nlp.get_export_data(fmt)
                    if export_data:
                        st.download_button(
                            label=f"Download as {fmt.upper()}",
                            data=export_data,
                            file_name=f"export.{fmt}",
                            mime="text/csv" if fmt == "csv" else "application/json" if fmt == "json" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.warning("No data available to export.")

    # --- JSON Persistence ---
    st.sidebar.subheader("Session State")
    if st.button("Save Session State"):
        session_state = {
            "operations_history": st.session_state["operations_history"],
            "last_result": st.session_state["last_result"]
        }
        with open(EXPORTS_PATH / "session_state.json", "w") as f:
            json.dump(session_state, f, indent=2)
        st.success("Session state saved to exports/session_state.json")

    uploaded_json = st.sidebar.file_uploader("Load Session State (JSON)", type=["json"])
    if uploaded_json:
        try:
            session_state = json.load(uploaded_json)
            st.session_state["operations_history"] = session_state.get("operations_history", [])
            st.session_state["last_result"] = session_state.get("last_result", None)
            if st.session_state["last_result"] and "result_data" in st.session_state["last_result"]:
                nlp.current_view = pd.DataFrame(st.session_state["last_result"]["result_data"])
            st.success("Session state loaded successfully!")
        except Exception as e:
            st.error(f"Error loading session state: {str(e)}")
