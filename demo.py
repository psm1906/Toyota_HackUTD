import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Function to load data from a link
def load_data_from_link(link):
    try:
        if link.endswith('.csv'):
            df = pd.read_csv(link)
        elif link.endswith('.xlsx'):
            df = pd.read_excel(link)
        elif 'docs.google.com/spreadsheets' in link:
            csv_url = link.replace('/edit#gid=', '/export?format=csv&gid=')
            df = pd.read_csv(csv_url)
        else:
            st.error("Unsupported file format! Please provide a valid link to a Google Sheet, CSV, or Excel file.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Function for data preprocessing
def preprocess_data(df):
    try:
        # Check for the 'Year' column
        if 'Year' in df.columns:
            df['Year'] = df['Year'].astype(str).str.replace(',', '').astype(int)
        else:
            st.error("The dataset must have a 'Year' column for analysis.")
            return None

        # Standardize column names
        df.columns = df.columns.str.strip()

        return df
    except Exception as e:
        st.error(f"Error preprocessing data: {e}")
        return None

# Function to create visualizations
def create_visualizations(df):
    try:
        # Ensure the data is sorted by Year
        df = df.sort_values(by='Year')

        st.subheader("Data Trends by Year")

        # Bar chart for counts per year
        st.write("### Vehicle Counts per Year")
        year_counts = df['Year'].value_counts().sort_index()

        # Matplotlib Bar Chart
        plt.figure(figsize=(10, 6))
        plt.bar(year_counts.index, year_counts.values, color='blue')
        plt.title('Vehicle Counts by Year')
        plt.xlabel('Year')
        plt.ylabel('Count')
        st.pyplot(plt.gcf())

        # Line Chart: Vehicle counts over the years
        st.write("### Vehicle Counts Trend Over the Years")
        plt.figure(figsize=(10, 6))
        year_counts.plot(kind='line', color='green', marker='o')
        plt.title('Trend of Vehicle Counts Over the Years')
        plt.xlabel('Year')
        plt.ylabel('Vehicle Count')
        st.pyplot(plt.gcf())

        # Scatter Plot: Compare Year vs Fuel Economy (or another continuous variable)
        if 'Fuel Economy' in df.columns:
            st.write("### Scatter Plot: Year vs. Fuel Economy")
            plt.figure(figsize=(10, 6))
            sns.scatterplot(x='Year', y='Fuel Economy', data=df, color='purple')
            plt.title('Fuel Economy Over the Years')
            plt.xlabel('Year')
            plt.ylabel('Fuel Economy')
            st.pyplot(plt.gcf())

        # Pie Chart for distribution of vehicle types
        if 'Vehicle Type' in df.columns:
            st.write("### Vehicle Types Distribution")
            vehicle_type_counts = df['Vehicle Type'].value_counts()
            plt.figure(figsize=(8, 8))
            vehicle_type_counts.plot(kind='pie', autopct='%1.1f%%', colors=['orange', 'yellow', 'green', 'blue'])
            plt.title('Vehicle Type Distribution')
            st.pyplot(plt.gcf())

        # Heatmap for correlation between numeric features (if available)
        st.write("### Correlation Heatmap for Numeric Features")
        numeric_df = df.select_dtypes(include=['float64', 'int64'])
        if len(numeric_df.columns) > 1:
            plt.figure(figsize=(10, 6))
            correlation = numeric_df.corr()
            sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
            plt.title('Correlation Heatmap')
            st.pyplot(plt.gcf())

    except Exception as e:
        st.error(f"Error creating visualizations: {e}")

# Streamlit App
def main():
    st.title("Toyota Vehicle Analysis (2021-2025)")

    st.write("""
    This app allows Toyota employees to analyze vehicle trends from 2021 to 2025. 
    Provide a link to your dataset (Google Sheets, CSV, or Excel), and visualize the trends interactively.
    """)

    # User Input: Link to dataset
    link = st.text_input("Enter the link to your dataset (Google Sheet, CSV, or Excel):")
    
    if link:
        st.write("Loading data...")
        df = load_data_from_link(link)
        
        if df is not None:
            st.write("Raw Data", df.head())
            
            # Preprocess data
            df = preprocess_data(df)
            
            if df is not None:
                st.write("Preprocessed Data", df.head())
                
                # Create visualizations
                create_visualizations(df)

# Run the app
if __name__ == "__main__":
    main()
