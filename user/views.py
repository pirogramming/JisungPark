from django.shortcuts import render
from allauth.account.views import LoginView, SignupView

def index(request):
    return render(request, 'account/login_done.html')

class CustomLoginView(LoginView):
    template_name = "user/login.html"  # 커스텀 템플릿 사용

class CustomSignupView(SignupView):
    template_name = "user/signup.html"