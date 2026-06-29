from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Post, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image_url']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'maxlength': 500, 'placeholder': 'Share something bright...', 'class': 'post-textarea'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'Optional image URL', 'class': 'image-url-input'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {'content': forms.TextInput(attrs={'maxlength': 300, 'placeholder': 'Write a comment...'})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'location', 'website']
