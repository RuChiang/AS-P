from django import forms

class AddUser(forms.Form):
    CLINIC_MANAGER = 'CM'
    DISPATCHER = 'DP'
    WAREHOUSE_PERSONNEL = 'WP'
    ROLES = (
        (CLINIC_MANAGER, 'Clinic Manager'),
        (DISPATCHER, 'Dispatcher'),
        (WAREHOUSE_PERSONNEL, 'Warehouse Personnel')
    )
    email = forms.EmailField(max_length = 254)
    role = forms.ChoiceField(choices = ROLES)
    # hospital = forms.CharField(label='hospital', max_length=50)

class SignupForm(forms.Form):

    first_name = forms.CharField(label='first name', max_length = 50)
    last_name = forms.CharField(label='last name', max_length = 50)
    username = forms.CharField(label='username', max_length = 50)
    password = forms.CharField(label='password', max_length = 32, widget=forms.PasswordInput)

class ClinicManagerSignupForm(SignupForm):
    hospital = forms.CharField(label='hospital', max_length = 50)


class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length = 50)
    password = forms.CharField(label='password', max_length = 32, widget=forms.PasswordInput)

class GetPassword(forms.Form):
    username = forms.CharField(label='username', max_length = 50)

class ResetPassword(forms.Form):
    password = forms.CharField(label='password', max_length = 32, widget=forms.PasswordInput)

class ManageAccountForm(forms.Form):
    email = forms.EmailField(max_length = 254, required=False)
    first_name = forms.CharField(label='first name', max_length = 50, required=False)
    last_name = forms.CharField(label='last name', max_length = 50, required=False)
    password = forms.CharField(label='password', max_length = 32, widget=forms.PasswordInput, required=False)
