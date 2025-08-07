import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Function Management", layout="wide")

# Backend URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5001")

st.title("🔧 Function Management")
st.markdown("---")

# Initialize session state
if 'functions' not in st.session_state:
    st.session_state.functions = []
if 'selected_function' not in st.session_state:
    st.session_state.selected_function = None

def fetch_functions():
    try:
        response = requests.get(f"{BACKEND_URL}/api/functions")
        if response.status_code == 200:
            st.session_state.functions = response.json()
        else:
            st.error(f"Failed to fetch functions: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

def create_function(name, route, language, timeout_ms, code):
    try:
        data = {
            "name": name,
            "route": route,
            "language": language,
            "timeout_ms": timeout_ms,
            "code": code
        }
        response = requests.post(f"{BACKEND_URL}/api/functions", json=data)
        if response.status_code == 201:
            st.success("Function created successfully!")
            fetch_functions()
            return True
        else:
            st.error(f"Failed to create function: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error creating function: {str(e)}")
        return False

def update_function(function_id, name, route, language, timeout_ms, code):
    try:
        data = {
            "name": name,
            "route": route,
            "language": language,
            "timeout_ms": timeout_ms,
            "code": code
        }
        response = requests.put(f"{BACKEND_URL}/api/functions/{function_id}", json=data)
        if response.status_code == 200:
            st.success("Function updated successfully!")
            fetch_functions()
            return True
        else:
            st.error(f"Failed to update function: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error updating function: {str(e)}")
        return False

def delete_function(function_id):
    try:
        response = requests.delete(f"{BACKEND_URL}/api/functions/{function_id}")
        if response.status_code == 200:
            st.success("Function deleted successfully!")
            fetch_functions()
            return True
        else:
            st.error(f"Failed to delete function: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error deleting function: {str(e)}")
        return False

# Fetch functions on page load
fetch_functions()

# Main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Function Form")
    
    # Form for creating/editing functions
    with st.form("function_form"):
        name = st.text_input("Function Name", value=st.session_state.selected_function['name'] if st.session_state.selected_function else "")
        route = st.text_input("Route", value=st.session_state.selected_function['route'] if st.session_state.selected_function else "")
        language = st.selectbox("Language", ["python", "javascript"], 
                               index=0 if not st.session_state.selected_function else 
                               (0 if st.session_state.selected_function['language'] == 'python' else 1))
        timeout_ms = st.number_input("Timeout (ms)", min_value=1000, max_value=300000, value=30000 if not st.session_state.selected_function else st.session_state.selected_function['timeout_ms'])
        
        # Code editor
        default_code = """# Python example
def main():
    return "Hello, World!"

if __name__ == "__main__":
    print(main())
""" if language == "python" else """// JavaScript example
function main() {
    return "Hello, World!";
}

console.log(main());
"""
        
        code = st.text_area("Code", height=300, 
                           value=st.session_state.selected_function['code'] if st.session_state.selected_function else default_code)
        
        col_create, col_update, col_clear = st.columns(3)
        
        with col_create:
            create_btn = st.form_submit_button("Create", type="primary")
        with col_update:
            update_btn = st.form_submit_button("Update", disabled=not st.session_state.selected_function)
        with col_clear:
            clear_btn = st.form_submit_button("Clear")
        
        if create_btn and name and route and code:
            create_function(name, route, language, timeout_ms, code)
        
        if update_btn and st.session_state.selected_function:
            update_function(st.session_state.selected_function['id'], name, route, language, timeout_ms, code)
        
        if clear_btn:
            st.session_state.selected_function = None
            st.experimental_rerun()

with col2:
    st.subheader("📋 Functions List")
    
    if st.button("🔄 Refresh"):
        fetch_functions()
    
    if st.session_state.functions:
        for func in st.session_state.functions:
            with st.expander(f"🔧 {func['name']} - {func['language']}"):
                st.write(f"**Route:** {func['route']}")
                st.write(f"**Timeout:** {func['timeout_ms']}ms")
                st.write(f"**Created:** {func['created_at']}")
                
                # Replace nested expander with toggle button
                show_code_key = f"show_code_{func['id']}"
                if st.button("👁️ Toggle Code View", key=f"toggle_code_{func['id']}"):
                    # Toggle the state
                    if show_code_key not in st.session_state:
                        st.session_state[show_code_key] = True
                    else:
                        st.session_state[show_code_key] = not st.session_state[show_code_key]
                
                # Show code if toggled on
                if st.session_state.get(show_code_key, False):
                    st.code(func['code'], language=func['language'])
                
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button("✏️ Edit", key=f"edit_{func['id']}"):
                        st.session_state.selected_function = func
                        st.experimental_rerun()
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"delete_{func['id']}", type="secondary"):
                        delete_function(func['id'])
    else:
        st.info("No functions found. Create your first function using the form on the left.")


st.markdown("---")
st.markdown("💡 **Tip**: Edit a function by clicking the 'Edit' button, then use 'Update' to save changes.")
