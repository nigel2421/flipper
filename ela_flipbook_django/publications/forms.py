# publications/forms.py

from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from .models import Profile 

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
    
      # --- ADD THIS NEW FIELD ---
    phone_number = forms.CharField(max_length=20, label='Phone Number (Optional)', required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Save the phone number to the user's profile
        user.profile.phone_number = self.cleaned_data['phone_number']
        user.profile.save()
        
        return user
    
    def __init__(self, *args, **kwargs):
        # --- ADD THIS LOGIC ---
        # Get the request object, which contains the URL parameters
        self.request = kwargs.pop('request', None)
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        
        # Get the referral code from the URL, if it exists
        referral_code = self.request.GET.get('ref')
        if referral_code:
            try:
                # Find the user who owns this referral code
                self.referrer = Profile.objects.get(referral_code=referral_code).user
            except Profile.DoesNotExist:
                self.referrer = None
        else:
            self.referrer = None
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        user.profile.phone_number = self.cleaned_data.get('phone_number')
        
        # --- ADD THIS LOGIC ---
        # If we found a valid referrer, save the relationship
        if hasattr(self, 'referrer') and self.referrer:
            user.profile.referred_by = self.referrer

        user.profile.save()
        
        return user