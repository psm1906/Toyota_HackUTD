import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
 
# Visualization features
plt.style.use('default')
sns.set_theme(style="whitegrid")

#Demo Link: https://docs.google.com/spreadsheets/d/e/2PACX-1vShOQ3Mn0sl6ZNCbFmSqeNugc2FzzLnvOFULvmdw0C3XDqtByuCTsPusHgjhdBYsxRymeOlPl3DraJJ/pub?gid=1795415372&single=true&output=csv
 
# Custom colors
TOYOTA_COLORS = ['#FF0000', '#808080', '#000000', '#0066CC', '#4B0082']
 
def load_and_preprocess_data(link):
    """Load and preprocess data with enhanced error handling."""
    try:
        if not link:
            st.warning("Provide a working data source link.")
            return None
            
        if link.endswith('.csv'):
            df = pd.read_csv(link)
        elif link.endswith('.xlsx'):
            df = pd.read_excel(link)
        elif 'docs.google.com/spreadsheets' in link:
            csv_url = link.replace('/edit#gid=', '/export?format=csv&gid=')
            df = pd.read_csv(csv_url)
        else:
            st.error("⚠️ This file format is unsupported! Please provide a link to a Google Sheet, CSV, or Excel file.")
            return None
        
        # Preprocess data
        df['Year'] = pd.to_numeric(df['Year'].astype(str).str.replace(',', ''), errors='coerce')
        df = df[(df['Year'] >= 2021) & (df['Year'] <= 2025)]
        df.columns = df.columns.str.strip()
        
        # Add derived metrics if possible
        if 'Price' in df.columns and 'Cost' in df.columns:
            df['Profit_Margin'] = ((df['Price'] - df['Cost']) / df['Price']) * 100
            
        if 'Sales' in df.columns:
            df['Sales_Category'] = pd.qcut(df['Sales'],
                                         q=4,
                                         labels=['Low', 'Medium', 'High', 'Very High'])
            
        st.success("✅ Data load processing successful!")
        return df
        
    except Exception as e:
        st.error(f"❌ Error in data processing: {str(e)}")
        return None
 
def create_interactive_visualizations(df):
    """Create interactive visualizations using plotly."""
    
    st.header("📊 Interactive Data Visualization Dashboard")
    
    # Sidebar for filtering
    st.sidebar.header("Filters")
    
    # Year filter
    selected_years = st.sidebar.multiselect(
        "Select Years",
        options=sorted(df['Year'].unique()),
        default=sorted(df['Year'].unique())
    )
    
    # Filter data based on selection
    filtered_df = df[df['Year'].isin(selected_years)]
    
    # 1. Overview Section
    st.subheader("📈 Overview Dashboard")
    
    # Create three columns for key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_vehicles = len(filtered_df)
        st.metric("Total Vehicles", f"{total_vehicles:,}")
        
    with col2:
        if 'Fuel Economy' in filtered_df.columns:
            avg_fuel_economy = filtered_df['Fuel Economy'].mean()
            st.metric("Average Fuel Economy", f"{avg_fuel_economy:.1f} MPG")
            
    with col3:
        if 'Price' in filtered_df.columns:
            avg_price = filtered_df['Price'].mean()
            st.metric("Average Price", f"${avg_price:,.2f}")
    
    # 2. Interactive Time Series Analysis
    st.subheader("📅 Time Series Analysis")
    
    tab1, tab2 = st.tabs(["Trend Analysis", "Distribution Analysis"])
    
    with tab1:
        # Interactive line chart, many metrics
        metrics_to_plot = [col for col in filtered_df.columns
                          if filtered_df[col].dtype in ['float64', 'int64']
                          and col != 'Year']
        
        selected_metric = st.selectbox(
            "Select Metrics for Analysis",
            options=metrics_to_plot
        )
        
        # Create interactive line chart
        fig = px.line(filtered_df,
                     x='Year',
                     y=selected_metric,
                     markers=True,
                     title=f'{selected_metric} Trend Over Time')
        
        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        # Interactive distribution plot
        fig = px.histogram(filtered_df,
                          x=selected_metric,
                          nbins=30,
                          title=f'Distribution of {selected_metric}')
        
        fig.update_layout(
            bargap=0.1,
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 3. Vehicle Type Analysis
    if 'Vehicle Type' in filtered_df.columns:
        st.subheader("Vehicle Type Analysis")
        
        tab1, tab2, tab3 = st.tabs(["Market Share", "Trends", "Comparison"])
        
        with tab1:
            # Interactive Pie Chart
            fig = px.pie(filtered_df,
                        names='Vehicle Type',
                        title='Vehicle Type Distribution',
                        hole=0.3)
            
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            # Stacked Area Chart
            vehicle_type_trends = pd.crosstab(filtered_df['Year'],
                                            filtered_df['Vehicle Type'],
                                            normalize='index') * 100
            
            fig = px.area(vehicle_type_trends,
                         title='Vehicle Type Trends Over Time')
            
            fig.update_layout(
                yaxis_title='Percentage (%)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with tab3:
            # Box plots for comparing metrics across vehicle types
            if len(metrics_to_plot) > 0:
                selected_compare_metric = st.selectbox(
                    "Select Metric for Comparison",
                    options=metrics_to_plot,
                    key='compare_metric'
                )
                
                fig = px.box(filtered_df,
                           x='Vehicle Type',
                           y=selected_compare_metric,
                           title=f'{selected_compare_metric} by Vehicle Type')
                
                st.plotly_chart(fig, use_container_width=True)
    
    # 4. Advanced Analytics
    st.subheader("🔍 Advanced Analytics")
    
    tab1, tab2 = st.tabs(["Correlation Analysis", "Scatter Matrix"])
    
    with tab1:
        # Interactive Correlation Heatmap
        numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_cols) > 1:
            correlation = filtered_df[numeric_cols].corr()
            
            fig = px.imshow(correlation,
                          labels=dict(color="Correlation"),
                          x=correlation.columns,
                          y=correlation.columns,
                          color_continuous_scale='RdBu')
            
            fig.update_layout(
                title='Interactive Correlation Heatmap',
                width=800,
                height=800
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    with tab2:
        # Interactive Scatter Matrix
        selected_metrics = st.multiselect(
            "Select Metrics for Scatter Matrix",
            options=metrics_to_plot,
            default=metrics_to_plot[:4] if len(metrics_to_plot) > 4 else metrics_to_plot
        )
        
        if len(selected_metrics) > 1:
            fig = px.scatter_matrix(filtered_df,
                                  dimensions=selected_metrics,
                                  color='Year' if 'Year' in filtered_df.columns else None)
            
            fig.update_layout(
                title='Interactive Scatter Matrix',
                width=1000,
                height=1000
            )
            
            st.plotly_chart(fig, use_container_width=True)

    
    # 6. Custom Analysis Section
    st.subheader("🎯 Custom Analysis")
    
    # Allow users to create custom visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Scatter Plot", "Bar Chart", "Line Chart", "Box Plot"]
        )
        
    with col2:
        color_variable = st.selectbox(
            "Select Color Variable (Optional)",
            ["None"] + list(filtered_df.columns)
        )
    
    x_axis = st.selectbox("Select X-axis", filtered_df.columns)
    y_axis = st.selectbox("Select Y-axis", filtered_df.columns)
    
    if chart_type == "Scatter Plot":
        fig = px.scatter(filtered_df,
                        x=x_axis,
                        y=y_axis,
                        color=None if color_variable == "None" else color_variable,
                        title=f'Custom Scatter Plot: {x_axis} vs {y_axis}')
    
    elif chart_type == "Bar Chart":
        fig = px.bar(filtered_df,
                    x=x_axis,
                    y=y_axis,
                    color=None if color_variable == "None" else color_variable,
                    title=f'Custom Bar Chart: {x_axis} vs {y_axis}')
    
    elif chart_type == "Line Chart":
        fig = px.line(filtered_df,
                     x=x_axis,
                     y=y_axis,
                     color=None if color_variable == "None" else color_variable,
                     title=f'Custom Line Chart: {x_axis} vs {y_axis}')
    
    else:  # Box Plot
        fig = px.box(filtered_df,
                    x=x_axis,
                    y=y_axis,
                    color=None if color_variable == "None" else color_variable,
                    title=f'Custom Box Plot: {x_axis} vs {y_axis}')
    
    st.plotly_chart(fig, use_container_width=True)
 
def main():
    st.set_page_config(page_title="Toyota Vehicle Analysis",
                      page_icon="🚗",
                      layout="wide",
                      initial_sidebar_state="expanded")
    
    st.title("🚗 Toyota Echo Vehicle Analysis Dashboard (2021-2025)")
    
    st.markdown("""
    ### Welcome to the Toyota Echo Dashboard!
    Upload your data and explore interactive visualizations with real-time filtering and custom analysis options.
    
    **Features:**
    - Real-time filtering by year and vehicle type
    - Interactive charts with hover details
    - Custom visualization builder
    - Advanced analytics and correlations
    """)
    
    # File upload section
    st.sidebar.subheader("📁 Data Upload")
    link = st.sidebar.text_input(
        "Enter your data source link:",
        placeholder="https://docs.google.com/spreadsheets/d/..."
    )
    
    if link:
        with st.spinner("Loading and processing your data..."):
            df = load_and_preprocess_data(link)
            
            if df is not None:
                with st.expander("👀 Preview Raw Data"):
                    st.dataframe(df.head())
                
                create_interactive_visualizations(df)
                
                # Download processed data option
                csv = df.to_csv(index=False)
                st.sidebar.download_button(
                    label="📥 Download Processed Data",
                    data=csv,
                    file_name="processed_toyota_data.csv",
                    mime="text/csv"
                )
 
if __name__ == "__main__":
    main()
