from django import forms
# from asp.models import Hospital
#
# def getHospitalNames():
#     hospitals = Hospital.objects.all()
#     NAMES = []
#     for hospital in hospitals:
#         NAMES.append((hospital.name, hospital.name))
#     return tuple(NAMES)

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

    first_name = forms.CharField(label='firstname', max_length = 50)
    last_name = forms.CharField(label='lastname', max_length = 50)
    username = forms.CharField(label='username', max_length = 50)
    password = forms.CharField(label='password', max_length = 50)
    hospital = forms.CharField(label='hospital', max_length = 50)
    email = forms.EmailField(max_length = 254)
    role = forms.ChoiceField(choices = ROLES)

class ClinicManegerSignupForm(SignupForm):
    hospital = forms.CharField(label='hospital', max_length = 50)


class LoginForm(forms.Form):
    username = forms.CharField(label='name', max_length = 50)
    password = forms.CharField(label='password', max_length = 50)
