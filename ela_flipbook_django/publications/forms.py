# publications/forms.py

from django import forms
from .models import Contributor

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


class ContributorForm(forms.ModelForm):
    class Meta:
        model = Contributor
        fields = ['full_name', 'email', 'phone_number', 'country', 'field_or_industry', 'submission_type', 'subject', 'message', 'attachment']
