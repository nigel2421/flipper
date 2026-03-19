# publications/forms.py

from django import forms
from .models import Magazine, Article, Comment, Rating, Profile, Contributor

class MagazineForm(forms.ModelForm):
    class Meta:
        model = Magazine
        fields = ['title', 'excerpt', 'pdf_file', 'cover_image']

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'excerpt', 'content', 'cover_image', 'tags', 'is_featured', 'is_editors_pick']

class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add a comment...'
            })
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.HiddenInput(),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'job_title', 'job_role', 'company', 'industry']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
        }

class ContributorForm(forms.ModelForm):
    class Meta:
        model = Contributor
        fields = ['full_name', 'email', 'submission_type', 'subject', 'message', 'field_or_industry', 'attachment', 'terms_and_conditions']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super(ContributorForm, self).__init__(*args, **kwargs)
        self.fields['message'].required = False
