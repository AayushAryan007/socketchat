from django import forms
from .models import Post, Comment, PostMedia

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "What's on your mind?"
            })
        }

class PostMediaForm(forms.ModelForm):
    class Meta:
        model = PostMedia
        fields = ['file', 'media_type']
        widgets = {
            'media_type': forms.Select(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...'
            })
        }