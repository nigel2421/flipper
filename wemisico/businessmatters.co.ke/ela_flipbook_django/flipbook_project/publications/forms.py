# publications/forms.py

from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from .models import Profile # Import the Profile model

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone_number = forms.CharField(max_length=20, label='Phone Number (Optional)', required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

        # --- THIS IS THE UPDATED __init__ METHOD ---
    def __init__(self, *args, **kwargs):
        # We still try to get the request, but we don't use it immediately.
        self.request = kwargs.pop('request', None)
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        
        # This is the guard clause. Only run this code if the request exists.
        if self.request:
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
        # Create the new user
        user = super(CustomSignupForm, self).save(request)
        
        # Save the extra data
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # The profile is created automatically by our signal.
        # We just need to update it.
        user.profile.phone_number = self.cleaned_data.get('phone_number')
        
        # If we found a valid referrer during __init__, save the relationship
        if hasattr(self, 'referrer') and self.referrer:
            user.profile.referred_by = self.referrer

        user.profile.save()
        
        return user