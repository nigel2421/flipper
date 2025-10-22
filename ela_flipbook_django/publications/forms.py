# publications/forms.py

from django import forms
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    # Add the fields you want to ask for
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    def save(self, request):
        # Call the parent class's save method to create the user
        user = super(CustomSignupForm, self).save(request)
        # Save the extra data to the user model
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user