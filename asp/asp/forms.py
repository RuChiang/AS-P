from django import forms

class SignupForm(forms.Form):
    CLINIC_MANAGER = 'CM'
    DISPATCHER = 'DP'
    WAREHOUSE_PERSONNEL = 'WP'
    ADMIN = 'AD'
    ROLES = (
        (CLINIC_MANAGER, 'Clinic Manager'),
        (DISPATCHER, 'Dispatcher'),
        (WAREHOUSE_PERSONNEL, 'Warehouse Personnel'),
        (ADMIN, 'Admin')
    )
    username = forms.CharField(label='name', max_length = 50)
    email = forms.EmailField(max_length = 254)
    hospital = forms.CharField(max_length = 50)
    role = forms.ChoiceField(choices = ROLES)
