import streamlit as st

st.set_page_config(
    page_title="Serverless Function Platform",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Serverless Function Execution Platform")
st.markdown("---")

st.markdown("""
## Welcome to the Serverless Function Platform

This platform allows you to:
- **Manage Functions**: Create, read, update, and delete serverless functions
- **Execute & Monitor**: Run functions in different virtualization environments and compare performance

### Navigation
Use the sidebar to navigate between different sections:
- **Function Management**: CRUD operations for your functions
- **Function Execution**: Execute functions and view performance metrics

### Supported Languages
- Python 🐍
- JavaScript 🟨

### Virtualization Technologies
- Docker 🐳
- gVisor 🔒
""")

st.markdown("---")
st.info("Select a page from the sidebar to get started!")
