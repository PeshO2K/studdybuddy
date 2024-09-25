import streamlit as st


def generic_form(location='main', fields=None, key='Sample Form'):
    
    if location == 'main':
        new_form = st.form(key=key,clear_on_submit=True)
    elif location == 'sidebar':
        new_form = st.sidebar.form(key=key, clear_on_submit=False)
    elif location == 'hidden':
        pass
    else:
        raise ValueError("Location must be main, sidebar or hidden")
    
    if fields is None:
        fields = {
            'Title': 'Sample Form',
            'Subtitles': ['Subtitle 1', 'Subtitle 2'],
            'Textfields':{
            'Username' : 'Username',
                            'Password': 'Password',
                             'Password': "Confirm Password" },
            'Button':'Submit'


        }
    if fields:
        values = {}
        for field_name, field_value in fields.items():
            if field_name =='Title':
                new_form.title(field_value)
            elif field_name == 'Subtitles':
                for subtitle in field_value:
                    new_form.subheader(subtitle)
            elif field_name == 'Textfields':
                for textfield in field_value:
                    # new_form.text_input(textfield, type='password' if textfield ==
                    #                     'Password' or textfield == 'Confirm Password' else 'default')
                    values[textfield] = new_form.text_input(textfield, type='password' if textfield ==
                                             'Password' or textfield == 'Confirm Password' else 'default')
        
        

                
        
        # submit = new_form.form_submit_button(fields['Button'])
        # new_form.link_button("SignUp Button",'Someurl')
        # form_buttons = new_form.container()

        # left, middle,right = form_buttons.columns(3,vertical_alignment="bottom")

        submit = new_form.form_submit_button(
            fields['Buttons']['Submit'], use_container_width=True)
        # secondary_button = right.markdown(
            # fields['Buttons']['Secondary'][0])
        

        values['submit'] = submit
        
    return values
            
            # st.text(f"{field_name}, {field_value}")
