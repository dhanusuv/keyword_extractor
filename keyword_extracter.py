import streamlit as st
import pandas as pd
import re

# Streamlit UI
st.title("Keyword Extraction")

# File uploader
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# Text input for keyword
keyword = st.text_input("Enter keyword to search (e.g., claimType)")

if uploaded_file and keyword:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)

    # Check if required columns exist
    if {"rule_id", "rule_desc"}.issubset(df.columns):
        extracted_data = {}

        for _, row in df.iterrows():
            rule_id = row["rule_id"]
            rule_desc = str(row["rule_desc"])  # Convert to string

            # Pattern 1: Extract values inside brackets (claimType in [OPT1450, ASC1450])
            pattern_brackets = rf"{re.escape(keyword)}\s*in\s*\[([^\]]+)\]"
            matches_brackets = re.findall(pattern_brackets, rule_desc, re.IGNORECASE)

            # Pattern 2: Extract values after "claimType is" (claimType is PRO1450)
            pattern_is = rf"{re.escape(keyword)}\s+is\s+(\w+)"
            matches_is = re.findall(pattern_is, rule_desc, re.IGNORECASE)

            # Collect matches
            values = set()
            for match in matches_brackets:
                values.update(v.strip() for v in match.split(","))
            for match in matches_is:
                values.add(match.strip())

            # Store results, combining multiple values into a single row
            if values:
                if rule_id in extracted_data:
                    extracted_data[rule_id].update(values)
                else:
                    extracted_data[rule_id] = set(values)

        # Convert dictionary to DataFrame
        output_df = pd.DataFrame([
            {"rule_id": rule_id, "rule_desc": ", ".join(sorted(values))}
            for rule_id, values in extracted_data.items()
        ])

        if not output_df.empty:
            # Display extracted results
            st.write("Filtered Results:", output_df)

            # Choose output format
            output_format = st.radio("Select output format", ("Excel", "CSV"))

            # Generate downloadable file
            if output_format == "Excel":
                output_file = "filtered_rules.xlsx"
                output_df.to_excel(output_file, index=False, engine="openpyxl")
            else:
                output_file = "filtered_rules.csv"
                output_df.to_csv(output_file, index=False)

            # Provide download link
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download Filtered Data",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if output_format == "Excel" else "text/csv"
                )
        else:
            st.warning("No matching rules found.")
    else:
        st.error("Uploaded file must have 'rule_id' and 'rule_desc' columns.")
