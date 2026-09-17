# gui/student_pages.py
import streamlit as st

def show_student_management_page(manager):
    """Renders all components for the student management page."""
    st.header("Student Management")

    # --- Section 1: Search for a Student ---
    st.subheader("Find a Student")
    search_term = st.text_input("Search by Name or ID")
    if search_term:
        # Call a find method on your manager and display results.
        # results = manager.find_students(search_term)
        # st.dataframe(results)
        pass

    # --- Section 2: Register a New Student ---
    st.subheader("Register a New Student")
    with st.form("registration_form"):
        reg_name = st.text_input("New Student Name")
        reg_instrument = st.text_input("First Instrument")
        submitted = st.form_submit_button("Register Student")
        
        if submitted:
            # Call the manager's method to perform the registration.
            # manager.register_new_student(reg_name, reg_instrument)
            st.success(f"Successfully registered {reg_name}!")