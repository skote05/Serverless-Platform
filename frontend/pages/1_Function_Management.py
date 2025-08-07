import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Function Management", layout="wide")

# Backend URL - Use environment variable instead of secrets
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
        # Add debug logging
        st.write("**Sending to backend:**")
        data = {
            "name": name,
            "route": route,
            "language": language,
            "timeout_ms": timeout_ms,
            "code": code
        }
        
        # Show first 100 characters of code being sent
        st.write(f"Code preview: {code[:100]}...")
        
        response = requests.post(f"{BACKEND_URL}/api/functions", json=data)
        
        if response.status_code == 201:
            st.success("Function created successfully!")
            fetch_functions()
            return True
        else:
            st.error(f"Failed to create function: {response.text}")
            # Also show what was actually sent
            st.write("**Data that was sent:**", data)
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
        timeout_ms = st.number_input("Timeout (ms)", min_value=1000, max_value=300000, 
                                    value=30000 if not st.session_state.selected_function else st.session_state.selected_function['timeout_ms'])
        
        # Code editor with dynamic default based on language
        if st.session_state.selected_function:
            # When editing, use the existing code
            default_code = st.session_state.selected_function['code']
        else:
            # When creating new, provide language-specific template
            if language == "python":
                default_code = """# Python example
def main():
    return "Hello, World!"

if __name__ == "__main__":
    print(main())"""
            else:
                default_code = """// JavaScript example
function main() {
    return "Hello, World!";
}

console.log(main());"""
        
        # Important: Use a unique key for the text area to prevent caching issues
        code_key = f"code_editor_{language}_{hash(str(st.session_state.selected_function)) if st.session_state.selected_function else 'new'}"
        
        code = st.text_area("Code", height=300, value=default_code, key=code_key)
        
        col_create, col_update, col_clear = st.columns(3)
        
        with col_create:
            create_btn = st.form_submit_button("Create", type="primary")
        with col_update:
            update_btn = st.form_submit_button("Update", disabled=not st.session_state.selected_function)
        with col_clear:
            clear_btn = st.form_submit_button("Clear")
        
        # Fix: Ensure all form data is properly captured for CREATE
        if create_btn:
            if name and route and code:
                # Debug: Log what we're actually sending
                st.write("**Debug Info:**")
                st.write(f"Name: {name}")
                st.write(f"Route: {route}")
                st.write(f"Language: {language}")
                st.write(f"Timeout: {timeout_ms}")
                st.write(f"Code length: {len(code)} characters")
                
                # Create function with explicitly captured form data
                success = create_function(name, route, language, timeout_ms, code)
                
                if success:
                    # Clear the form after successful creation
                    st.session_state.selected_function = None
                    st.experimental_rerun()
            else:
                st.error("Please fill in all required fields (name, route, and code)")
        
        if update_btn and st.session_state.selected_function:
            # Update works fine, keep as is
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
                
                # Show code directly without nested expander to avoid Streamlit error
                st.subheader("📄 Code:")
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
