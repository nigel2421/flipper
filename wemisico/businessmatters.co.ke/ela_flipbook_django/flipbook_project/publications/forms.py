# publications/forms.py

from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from .models import Profile

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone_number = forms.CharField(max_length=20, label='Phone Number (Optional)', required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

    def save(self, request):
        # Create the new user first
        user = super(CustomSignupForm, self).save(request)
        
        # Save the extra data from the form
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # The profile is created automatically by our signal.
        # We just need to update it.
        user.profile.phone_number = self.cleaned_data.get('phone_number')
        
        # --- THIS IS THE NEW, MORE ROBUST LOGIC ---
        # Get the referral code from the session if it exists
        referral_code = request.session.get('referral_code')
        if referral_code:
            try:
                # Find the user who owns this referral code
                referrer_profile = Profile.objects.get(referral_code=referral_code)
                # Save the relationship
                user.profile.referred_by = referrer_profile.user
                # Clear the referral code from the session so it's only used once
                del request.session['referral_code']
            except Profile.DoesNotExist:
                # If the code is invalid, do nothing
                pass

        user.profile.save()
        
        return user