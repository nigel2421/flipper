# publications/forms.py

from django import forms
from allauth.account.forms import SignupForm
from .models import Profile

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone_number = forms.CharField(max_length=20, label='Phone Number (optional)', required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

    def save(self, request):
        # Create the new user using allauth's standard process
        user = super(CustomSignupForm, self).save(request)
        
        # Save the extra data from our form
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Update the profile (which was created automatically by our signal)
        user.profile.phone_number = self.cleaned_data.get('phone_number')
        
        # --- THIS IS THE NEW, GUARANTEED LOGIC ---
        # Get the referral code from the session that we stored in the view
        referral_code = request.session.get('referral_code')
        if referral_code:
            try:
                referrer_profile = Profile.objects.get(referral_code=referral_code)
                # Save the relationship
                user.profile.referred_by = referrer_profile.user
                # Important: Clear the code from the session so it's only used once
                del request.session['referral_code']
            except Profile.DoesNotExist:
                # If the code is invalid for any reason, do nothing
                pass

        user.profile.save()
        
        return user