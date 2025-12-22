# publications/forms.py

from django import forms

class RatingForm(forms.Form):
    # The score will be set by JavaScript, so we use a hidden input.
    score = forms.IntegerField(widget=forms.HiddenInput(), min_value=1, max_value=5)


class CommentForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Add a comment:'
    )
    # Hidden field to store the ID of the parent comment for replies
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'comment-textarea'})


class ContributorForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your Name")
    email = forms.EmailField(label="Enter your email")
    phone_number = forms.CharField(max_length=20, label="Enter your phone number (Preferably Whatsapp Number)")
    expertise = forms.CharField(max_length=100, label="Enter your Expertise Industry/ Field")
    company = forms.CharField(max_length=100, required=False, label="Company Name (If joining on behalf of a company)")
    linkedin = forms.URLField(required=False, label="Enter your LinkedIn Profile Link")
