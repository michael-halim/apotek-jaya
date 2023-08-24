from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View

from .forms import CreateUserForm

def error_404_view(request, exception):
    """Handles Not Found Error"""
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')

def error_500_view(request):
    """Handles Server Error"""
    return render(request, '500.html')

class HomeView(LoginRequiredMixin, TemplateView):
    """Handles Home Page"""

    template_name = 'main_app/index.html'
    login_url = '/login/'

class LoginPageView(View):
    login_url = '/login/'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('main_app:home')
        
        form = CreateUserForm()
        context = {
            'form':form,
            'input_username':'',
        }

        return render(request,'main_app/login.html',context)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('main_app:home')
        
        messages.error(request,'Username or Password is incorrect')
        input_username = username
        form = CreateUserForm()

        context = { 
            'form':form ,
            'input_username':input_username, 
        }
    
        return render(request,'main_app/login.html',context)

def logoutPage(request):
    logout(request)
    return redirect('main_app:login')