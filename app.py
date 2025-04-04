import streamlit as st
import pandas as pd
import plotly.express as px
import xlrd  # Required for XLS file compatibility

# Custom sorting function to extract month and year and convert to a sortable format
def custom_sort(date_str):
    try:
        return pd.to_datetime(date_str, format="%b-%y")
    except ValueError:
        return date_str

# Set the title of your app
st.title("Interactive Plotly Charts with Streamlit")
st.write("Hello Data Nerd! 🤓")

# Sample dataset
# Sample dataset
data = {
    'Continent': ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania'],
    'Population': [6187585961, 7351438499, 30507333902, 6181115304, 212992136]
}

sample_df = pd.DataFrame(data)


# Option to upload CSV, XLS, or XLSX file
uploaded_file = st.file_uploader("Upload a Data File", type=["csv", "xlsx", "xls"])

# Process data based on user input
df = None

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='xlrd')
        st.write("Uploaded Data (First 5 Rows):")
        st.write(df.head())

    except pd.errors.EmptyDataError:
        st.warning("The uploaded file is empty.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    # Display the "Manually Enter Data" and "Use Sample Dataset" checkboxes
    data_input_method = st.radio("Choose Data Input Method", ("Manually Enter Data", "Use Sample Dataset"), index=1)
    
    if data_input_method == "Manually Enter Data":
        st.header("Enter Data Manually")
        x_values = st.text_area("Enter X-axis data (comma-separated)")
        y_values = st.text_area("Enter Y-axis data (comma-separated)")

        if x_values and y_values:
            x_list = x_values.split(",")
            y_list = y_values.split(",")
            # Convert the y-values to numeric
            y_list = [float(val) for val in y_list]
            df = pd.DataFrame({"X-axis": x_list, "Y-axis": y_list})

    else:
        df = sample_df


# If data is available, proceed with plotting
if df is not None and not df.empty:
    # Select X and Y columns from the data
    x_column = st.selectbox("Select X-axis data", df.columns)
    y_column = st.selectbox("Select Y-axis data", df.columns, index = 1) #Index is used to select second column default
    
    # Convert x-axis data to numeric if it's numeric
    if pd.api.types.is_numeric_dtype(df[x_column].dtype):
        df[x_column] = df[x_column].astype(float)

    if df[x_column].dtype == 'object':
        df[x_column] = df[x_column].apply(custom_sort)

    # Aggregate data based on the x-axis (e.g., sum values for the same year)
    df = df.groupby(x_column, as_index=False).agg({y_column: 'sum'})

    df = df.sort_values(by=[x_column], key=custom_sort)

    chart_title = f"{x_column} vs {y_column}"

    labels = {}

    # Allow users to set a custom chart title
    custom_chart_title = st.text_input("Custom Chart Title", chart_title)

    # Allow users to switch the x and y axes
    switch_axes = st.checkbox("Switch X and Y axis")

    if switch_axes:
        x_column, y_column = y_column, x_column  # Swap x and y

    # Allow users to choose colors
    color_option = st.checkbox("Apply Colors", value=True)
    if color_option:
        color_column = st.selectbox("Select Color Column", df.columns)
    else:
        color_column = None

    chart_type = st.selectbox("Select Chart Type", ["bar","scatter", "line", "area", "box", "treemap", "pie", "bubble", "scatter3d", "line3d"])

    if chart_type == "scatter":
        fig = px.scatter(df, x=x_column, y=y_column, title=custom_chart_title, labels=labels, color=color_column)
    elif chart_type ==  "line":
        fig = px.line(df, x=x_column, y=y_column, title=custom_chart_title, labels=labels)
    elif chart_type == "bar":
        fig = px.bar(df, x=x_column, y=y_column, title=custom_chart_title, labels=labels, color=color_column)
    elif chart_type == "area":
        fig = px.area(df, x=x_column, y=y_column, title=custom_chart_title, labels=labels, color=color_column)
    elif chart_type == "box":
        fig = px.box(df, x=x_column, y=y_column, title=custom_chart_title, labels=labels, color=color_column)
    elif chart_type == "treemap":
        fig = px.treemap(df, path=[x_column], values=y_column, title=custom_chart_title, labels=labels, color=color_column)
    elif chart_type == "pie":
        fig = px.pie(df, names=x_column, values=y_column, title=custom_chart_title, labels=labels, color=color_column)
    elif chart_type == "bubble":
        fig = px.scatter(df, x=x_column, y=y_column, size=y_column, title=custom_chart_title, labels=labels, color=color_column)
    elif chart_type == "scatter3d":
        fig = px.scatter_3d(df, x=x_column, y=y_column, z=y_column, title=custom_chart_title, labels=labels, color=color_column)
    elif chart_type == "line3d":
        fig = px.line_3d(df, x=x_column, y=y_column, z=y_column, title=custom_chart_title, labels=labels)
    st.plotly_chart(fig)

    # Show all data using a checkbox
    show_all_data = st.checkbox("Data Summary Stats")
    if show_all_data and df is not None and not df.empty:
        st.subheader("Data Summary Statistics")
        st.write(df.describe())
    show_all_data2 = st.checkbox("Show All Data At Bottom")
    if show_all_data2 and df is not None and not df.empty:
        st.write("Entire Data:")
        st.write(df)
