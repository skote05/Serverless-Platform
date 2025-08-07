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
    
import time

def create_function_with_debug(name, route, language, timeout_ms, code):
    try:
        # Comprehensive debugging
        st.write("📡 **FRONTEND → BACKEND COMMUNICATION:**")
        
        payload = {
            "name": name,
            "route": route,
            "language": language,
            "timeout_ms": timeout_ms,
            "code": code
        }
        
        st.write(f"7. Payload prepared:")
        st.write(f"   - Name: {payload['name']}")
        st.write(f"   - Route: {payload['route']}")
        st.write(f"   - Language: {payload['language']}")
        st.write(f"   - Timeout: {payload['timeout_ms']}")
        st.write(f"   - Code length: {len(payload['code'])}")
        st.write(f"   - Code preview: {repr(payload['code'][:100])}")
        
        st.write("8. Sending POST request...")
        response = requests.post(f"{BACKEND_URL}/api/functions", json=payload)
        
        st.write(f"9. Response status: {response.status_code}")
        
        if response.status_code == 201:
            st.success("✅ Function created successfully!")
            response_data = response.json()
            st.write("10. Created function data:")
            st.write(f"   - ID: {response_data.get('id')}")
            st.write(f"   - Stored code length: {len(response_data.get('code', ''))}")
            st.write(f"   - Stored code preview: {repr(response_data.get('code', '')[:100])}")
            
            fetch_functions()
            return True
        else:
            st.error(f"❌ Backend error: {response.text}")
            st.write("10. Error response:", response.text)
            return False
            
    except Exception as e:
        st.error(f"❌ Frontend error: {str(e)}")
        return False


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
        
        # CRITICAL FIX: Don't set default_code in text_area value during CREATE
        if st.session_state.selected_function:
            # EDITING: Use existing code
            initial_code = st.session_state.selected_function['code']
            st.info("📝 **Editing Mode** - Modify the code below:")
        else:
            # CREATING: Start with empty or minimal code
            initial_code = ""
            st.info("✨ **Creating New Function** - Write your code below:")
            
            # Show template as reference, but don't put it in the text area
            if language == "python":
                template_code = """# Python template (replace with your code):
    def main():
        return "Hello, World!"

    if __name__ == "__main__":
        print(main())"""
            else:
                template_code = """// JavaScript template (replace with your code):
    function main() {
        return "Hello, World!";
    }

    console.log(main());"""
            
            with st.expander("📖 Click to see template code (copy if needed)"):
                st.code(template_code, language=language)
        
        # Use unique key and get actual user input
        code_key = f"code_input_{language}_{int(time.time() * 1000) % 10000}"
        code = st.text_area("Code", height=300, value=initial_code, key=code_key, placeholder="Write your function code here...")
        
        # Real-time code preview
        if code and code.strip():
            st.write(f"**Live Preview** ({len(code)} characters):")
            st.code(code[:200] + ("..." if len(code) > 200 else ""), language=language)
        
        col_create, col_update, col_clear = st.columns(3)
        
        with col_create:
            create_btn = st.form_submit_button("Create", type="primary")
        with col_update:
            update_btn = st.form_submit_button("Update", disabled=not st.session_state.selected_function)
        with col_clear:
            clear_btn = st.form_submit_button("Clear")
        
        # Enhanced CREATE with step-by-step debugging
        if create_btn:
            st.write("🔍 **CREATE OPERATION DEBUG:**")
            st.write(f"1. Form submitted with name: '{name}'")
            st.write(f"2. Route: '{route}'")
            st.write(f"3. Language: '{language}'")
            st.write(f"4. Code captured: {len(code)} characters")
            st.write(f"5. Code starts with: '{code[:50]}...'")
            
            if not code or code.strip() == "":
                st.error("❌ No code provided! Please write your function code.")
            elif name and route:
                st.write("6. Sending to backend...")
                
                # Create function with debugging
                success = create_function_with_debug(name, route, language, timeout_ms, code)
                
                if success:
                    st.session_state.selected_function = None
                    st.experimental_rerun()
            else:
                st.error("❌ Please fill in all required fields")
        
        if update_btn and st.session_state.selected_function:
            st.write("🔄 **UPDATE OPERATION:**")
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
