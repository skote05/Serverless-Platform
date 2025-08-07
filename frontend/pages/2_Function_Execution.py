import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Function Execution", layout="wide")

# Backend URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5001")

st.title("⚡ Function Execution & Monitoring")
st.markdown("---")

# Initialize session state
if 'execution_results' not in st.session_state:
    st.session_state.execution_results = {}
if 'functions' not in st.session_state:
    st.session_state.functions = []

def fetch_functions():
    try:
        response = requests.get(f"{BACKEND_URL}/api/functions")
        if response.status_code == 200:
            st.session_state.functions = response.json()
        else:
            st.error(f"Failed to fetch functions: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

def execute_function(function_id, executors):
    try:
        with st.spinner(f"Executing function with {', '.join(executors)}..."):
            data = {"executors": executors}
            response = requests.post(f"{BACKEND_URL}/api/functions/{function_id}/execute", json=data)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to execute function: {response.text}")
                return None
    except Exception as e:
        st.error(f"Error executing function: {str(e)}")
        return None

def fetch_metrics(function_id):
    try:
        response = requests.get(f"{BACKEND_URL}/api/functions/{function_id}/metrics")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch metrics: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error fetching metrics: {str(e)}")
        return []

# Fetch functions on page load
fetch_functions()

if not st.session_state.functions:
    st.warning("No functions available. Please create functions in the Function Management page first.")
    st.stop()

# Function selection
st.subheader("🎯 Select Function to Execute")
function_options = {f"{func['name']} ({func['language']})": func for func in st.session_state.functions}
selected_function_name = st.selectbox("Choose a function:", list(function_options.keys()))
selected_function = function_options[selected_function_name]

# Executor selection
st.subheader("🔧 Select Execution Environments")
col1, col2 = st.columns(2)
with col1:
    use_docker = st.checkbox("Docker 🐳", value=True)
with col2:
    use_gvisor = st.checkbox("gVisor 🔒", value=True)

executors = []
if use_docker:
    executors.append("docker")
if use_gvisor:
    executors.append("gvisor")

if not executors:
    st.warning("Please select at least one execution environment.")
    st.stop()

# Execution button
if st.button("🚀 Execute Function", type="primary", disabled=not executors):
    results = execute_function(selected_function['id'], executors)
    if results:
        st.session_state.execution_results = results

# Display execution results
if st.session_state.execution_results:
    st.markdown("---")
    st.subheader("📊 Execution Results")
    
    results = st.session_state.execution_results
    
    # Create comparison table
    comparison_data = []
    for executor, result in results.items():
        comparison_data.append({
            "Executor": executor.capitalize(),
            "Status": result.get('status', 'unknown'),
            "Execution Time (ms)": f"{result.get('execution_time_ms', 0):.2f}",
            "Memory Usage (MB)": f"{result.get('memory_usage_mb', 0):.2f}",
            "CPU Usage (%)": f"{result.get('cpu_usage_percent', 0):.2f}",
        })
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    
    # Create visualizations
    st.subheader("📈 Performance Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Execution time chart
        exec_times = [results[executor].get('execution_time_ms', 0) for executor in executors]
        fig_time = go.Figure(data=[
            go.Bar(x=[e.capitalize() for e in executors], y=exec_times, 
                  marker_color=['#1f77b4', '#ff7f0e'][:len(executors)])
        ])
        fig_time.update_layout(title="Execution Time (ms)", yaxis_title="Time (ms)")
        st.plotly_chart(fig_time, use_container_width=True)
    
    with col2:
        # Memory usage chart
        memory_usage = [results[executor].get('memory_usage_mb', 0) for executor in executors]
        fig_memory = go.Figure(data=[
            go.Bar(x=[e.capitalize() for e in executors], y=memory_usage,
                  marker_color=['#2ca02c', '#d62728'][:len(executors)])
        ])
        fig_memory.update_layout(title="Memory Usage (MB)", yaxis_title="Memory (MB)")
        st.plotly_chart(fig_memory, use_container_width=True)
    
    with col3:
        # CPU usage chart
        cpu_usage = [results[executor].get('cpu_usage_percent', 0) for executor in executors]
        fig_cpu = go.Figure(data=[
            go.Bar(x=[e.capitalize() for e in executors], y=cpu_usage,
                  marker_color=['#9467bd', '#8c564b'][:len(executors)])
        ])
        fig_cpu.update_layout(title="CPU Usage (%)", yaxis_title="CPU (%)")
        st.plotly_chart(fig_cpu, use_container_width=True)
    
    # Show detailed output/errors
    st.subheader("📄 Execution Details")
    for executor, result in results.items():
        with st.expander(f"{executor.capitalize()} Details"):
            if result.get('status') == 'success':
                st.success(f"Status: {result.get('status').upper()}")
                if result.get('output'):
                    st.subheader("Output:")
                    st.code(result.get('output'))
            else:
                st.error(f"Status: {result.get('status').upper()}")
                if result.get('error_message'):
                    st.subheader("Error:")
                    st.code(result.get('error_message'))

# Historical metrics
st.markdown("---")
st.subheader("📊 Historical Performance")

if st.button("📈 Load Historical Data"):
    metrics = fetch_metrics(selected_function['id'])
    
    if metrics:
        # Convert to DataFrame
        df_metrics = pd.DataFrame(metrics)
        df_metrics['executed_at'] = pd.to_datetime(df_metrics['executed_at'])
        
        # Group by executor type
        docker_metrics = df_metrics[df_metrics['executor_type'] == 'docker']
        gvisor_metrics = df_metrics[df_metrics['executor_type'] == 'gvisor']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🐳 Docker Performance Over Time")
            if not docker_metrics.empty:
                fig_docker = go.Figure()
                fig_docker.add_trace(go.Scatter(
                    x=docker_metrics['executed_at'], 
                    y=docker_metrics['execution_time_ms'],
                    mode='lines+markers',
                    name='Execution Time (ms)',
                    line=dict(color='#1f77b4')
                ))
                fig_docker.update_layout(
                    title="Docker Execution Time Trend",
                    xaxis_title="Time",
                    yaxis_title="Execution Time (ms)"
                )
                st.plotly_chart(fig_docker, use_container_width=True)
            else:
                st.info("No Docker metrics available")
        
        with col2:
            st.subheader("🔒 gVisor Performance Over Time")
            if not gvisor_metrics.empty:
                fig_gvisor = go.Figure()
                fig_gvisor.add_trace(go.Scatter(
                    x=gvisor_metrics['executed_at'], 
                    y=gvisor_metrics['execution_time_ms'],
                    mode='lines+markers',
                    name='Execution Time (ms)',
                    line=dict(color='#ff7f0e')
                ))
                fig_gvisor.update_layout(
                    title="gVisor Execution Time Trend",
                    xaxis_title="Time",
                    yaxis_title="Execution Time (ms)"
                )
                st.plotly_chart(fig_gvisor, use_container_width=True)
            else:
                st.info("No gVisor metrics available")
        
        # Summary statistics
        st.subheader("📈 Performance Summary")
        if not df_metrics.empty:
            summary_data = df_metrics.groupby('executor_type').agg({
                'execution_time_ms': ['mean', 'min', 'max', 'std'],
                'memory_usage_mb': ['mean', 'min', 'max'],
                'cpu_usage_percent': ['mean', 'min', 'max']
            }).round(2)
            
            st.dataframe(summary_data, use_container_width=True)
    else:
        st.info("No historical metrics available for this function.")

st.markdown("---")
st.markdown("💡 **Tip**: Execute functions multiple times to build up historical performance data for better analysis.")
