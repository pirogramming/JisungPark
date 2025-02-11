from django import forms
from .models import Review, Comment
from user.models import User

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': '댓글을 입력하세요...'}),
        }

class MyInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email', 'phonenumber']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': '이름을 입력하세요...'}),
            'email': forms.EmailInput(attrs={'placeholder': '이메일을 입력하세요...'}),
            'phonenumber': forms.TextInput(attrs={'placeholder': '전화번호를 입력하세요...'}),
        }