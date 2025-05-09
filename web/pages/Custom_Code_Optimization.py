import streamlit as st

# Load external CSS
st.set_page_config(page_title="Custom Code Optimization", layout="wide")
st.sidebar.header("Custom Code Optimization")
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("static/style.css")

# Add custom header to the top bar
st.markdown(
    """
    <div class="custom-header">
        🛠️ Custom Code Optimization
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### Submit Custom Code Optimization Request")

with st.form("custom_opt_form"):
    repo_name = st.text_input("Repository Name")
    file_path = st.text_input("File Path")
    custom_instructions = st.text_area("Custom Instructions", height=200)
    submit_btn = st.form_submit_button("Submit Optimization Request")
    if submit_btn:
        if repo_name and file_path and custom_instructions:
            st.success(f"Optimization request for `{file_path}` in repo `{repo_name}` submitted!")
            st.balloons()
        else:
            st.error("Please fill in all fields before submitting.")

# Footer
st.markdown("<div class='footer'>Made with ❤️ by CodeBrew</div>", unsafe_allow_html=True) 