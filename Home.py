
import streamlit as st
import auth_functions
import datetime
from st_pages import Page, show_pages, add_page_title, hide_pages

# st.set_page_config(initial_sidebar_state="collapsed")

# st.markdown(
#     """
# <style>
#     [data-testid="collapsedControl"] {
#         display: none
#     }
# </style>
# """,
#     unsafe_allow_html=True,
# )

def run():
    st.set_page_config(
        page_title="T7 Journal",
        page_icon="🏠",
)
    
show_pages(
    [
        Page("pages/t7journal.py", "T7 Journal", "📚"),
        Page("Home.py", "Home","🏠"),
    ]
)



## -------------------------------------------------------------------------------------------------
## Not logged in -----------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
if 'user_info' not in st.session_state:      
    st.markdown("<h1 style='text-align: center; font-weight: bold; color: black;'>User</h1>",unsafe_allow_html=True)   
    col1,col2,col3 = st.columns([1,2,1])
    # Authentication form layout
    do_you_have_an_account = col2.selectbox(label='Do you have an account?',options=('Yes','No','I forgot my password'))
    auth_form = col2.form(key='Authentication form',clear_on_submit=False)
    email = auth_form.text_input(label='Email')
    password = auth_form.text_input(label='Password',type='password') if do_you_have_an_account in {'Yes','No'} else auth_form.empty()
    auth_notification = col2.empty()    

    # Sign In
    if do_you_have_an_account == 'Yes' and auth_form.form_submit_button(label='Sign In',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Signing in'):
            auth_functions.sign_in(email,password)

    # Create Account
    elif do_you_have_an_account == 'No' and auth_form.form_submit_button(label='Create Account',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Creating account'):
            auth_functions.create_account(email,password)

    # Password Reset
    elif do_you_have_an_account == 'I forgot my password' and auth_form.form_submit_button(label='Send Password Reset Email',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Sending password reset link'):
            auth_functions.reset_password(email)

    # Authentication success and warning messages
    if 'auth_success' in st.session_state:       
        auth_notification.success(st.session_state.auth_success)
        del st.session_state.auth_success           
        
    elif 'auth_warning' in st.session_state:
        auth_notification.warning(st.session_state.auth_warning)
        del st.session_state.auth_warning
    
    if 'user_info' in st.session_state:
        st.rerun() 

## -------------------------------------------------------------------------------------------------
## Logged in --------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
else:
    # Show user information
    st.header('User Profile',divider="blue")
    with st.container(border=False):        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<p style='text-align: left; font-weight: bold; color: black;'>Email</p>",unsafe_allow_html=True)
            st.markdown("<p style='text-align: left; font-weight: bold; color: black;'>Account Created On</p>",unsafe_allow_html=True)        
            st.markdown("<p style='text-align: left; font-weight: bold; color: black;'>Account Verified</p>",unsafe_allow_html=True)
            st.markdown("<p style='text-align: left; font-weight: bold; color: black;'>Password Updated On</p>",unsafe_allow_html=True)
            st.markdown("<p style='text-align: left; font-weight: bold; color: black;'>Last Login At</p>",unsafe_allow_html=True)
        
        with col2: 
            st.markdown("<p style='text-align: left; color: black;'>"+ st.session_state.user_info["email"]+ " </p>",unsafe_allow_html=True) 
            st.markdown("<p style='text-align: left; color: black;'>"+  datetime.datetime.fromtimestamp(int(st.session_state.user_info["createdAt"])/1000).strftime("%B %d, %Y")+ " </p>",unsafe_allow_html=True) 
            st.markdown("<p style='text-align: left; color: black;'>"+ str(st.session_state.user_info["emailVerified"])+ " </p>",unsafe_allow_html=True) 
            st.markdown("<p style='text-align: left; color: black;'>"+  datetime.datetime.fromtimestamp(int(st.session_state.user_info["passwordUpdatedAt"])/1000).strftime("%B %d, %Y")+ " </p>",unsafe_allow_html=True) 
            st.markdown("<p style='text-align: left; color: black;'>"+  datetime.datetime.fromtimestamp(int(st.session_state.user_info["lastLoginAt"])/1000).strftime("%B %d, %Y")+ " </p>",unsafe_allow_html=True) 
    # st.write(st.session_state.user_info)

    # Sign out
    st.header('Sign out',divider="green")
    st.button(label='Sign Out',on_click=auth_functions.sign_out,type='primary')

    # Delete Account
    st.header('Delete account',divider="orange")
    password = st.text_input(label='Confirm your password',type='password')
    st.button(label='Delete Account',on_click=auth_functions.delete_account,args=[password],type='primary')    
    # st.switch_page("pages/t7journal.py")


