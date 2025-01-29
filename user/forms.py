from django import forms
from allauth.account.forms import SignupForm
from allauth.account.forms import LoginForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from user.models import User

class MyCustomLoginForm(LoginForm):
  # 추가하고 싶은 필드
    #remember_me = forms.BooleanField(required=False, initial=False)
    
    
    def __init__(self, *args, **kwargs):
        super(MyCustomLoginForm, self).__init__(*args, **kwargs)

        #del self.fields['remember']
        self.fields["password"].help_text = ''

    def clean_username(self):
        
        username = self.cleaned_data.get('username')
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            raise ValidationError("존재하지 않는 아이디입니다.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        # 필요한 추가 유효성 검사
        if self.cleaned_data.get("username") and self.cleaned_data.get("password"):
            user = self.user_cache
            if not user.is_active:
                raise ValidationError("이 계정은 활성화되지 않았습니다.")
        return cleaned_data


class MyCustomSignupForm(SignupForm):
    # 기존 필드 제거 후 새 필드 추가
    phonenumber = forms.CharField(
        max_length=20,
        label='전화번호',
        widget=forms.TextInput(attrs={'placeholder': '전화번호를 입력하세요'}),
    )

    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = '이메일 주소(필수)'

    def clean_phonenumber(self):
        """전화번호 중복 확인 로직 추가"""
        phonenumber = self.cleaned_data.get('phonenumber')
        if User.objects.filter(phonenumber=phonenumber).exists():
            raise ValidationError("이미 사용 중인 전화번호입니다. 다른 번호를 입력하세요.")
        return phonenumber

    def save(self, request):
        """전화번호와 사용자명을 저장하는 커스텀 로직"""
        user = super(MyCustomSignupForm, self).save(request)
        user.phonenumber = self.cleaned_data['phonenumber']
        user.username = self.cleaned_data.get('username', '')  # username도 검증
        user.save()
        return user
