from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger,EmptyPage
from django.utils.datastructures import MultiValueDictKeyError

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View, TemplateView

from .forms import CreateUserForm
from .decorators import unauthenticated_user
import pandas as pd
from django.views.generic.edit import FormView
from .forms import FileFieldForm
from .models import UploadFile

def error_404_view(request, exception):
    """Handles Not Found Error"""
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')

def error_500_view(request):
    """Handles Server Error"""
    return render(request, '500.html')

class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "main_app/upload.html"  # Replace with your template.
    success_url = 'main_app/upload_success'
     
    def post(self, request, *args, **kwargs):
        print('INSIDE')
        print(request.POST)
        print(request.FILES)
        form = FileFieldForm(request.POST, request.FILES)
        print(form)    
        if form.is_valid():
            files = request.FILES.getlist('file_upload')
            for f in files:
                UploadFile.objects.create(files=f)

            return render(request,'main_app/upload_success.html',{})
        else:
            return render(request,'main_app/upload_fail.html',{})
        
# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    """Handles Home Page"""

    template_name = 'main_app/index.html'
    login_url = '/login/'

@unauthenticated_user
def loginPage(request):
    """Handle Login Page"""
    # margin-left: -50%; -> Signup Tab
    # margin-left: 0%; -> Login Tab
    margin_left = 0
    form = None
    input_username = ''
    if request.method == 'POST':

        # Get Password and Confirm Password
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
    
        if password1 is not None and password2 is not None:
            # Signup
            form = CreateUserForm(request.POST or None)
            margin_left = -50

            if form.is_valid():
                # Succesfuly Create User
                form.save()
                margin_left = 0
                messages.info(request,'Your Account Has Been Created')

        else:
            # Login
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('main_app:home')

            # Error When Login
            messages.error(request,'Username or Password is incorrect')
            input_username = username
            margin_left = 0
            form = CreateUserForm()
    else:
        form = CreateUserForm()

    context = { 'form':form ,
                'margin_left':margin_left,
                'input_username':input_username, }
    
    return render(request,'main_app/login.html',context)

def logoutPage(request):
    logout(request)
    return redirect('main_app:login')