import random

from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from google_auth_httplib2 import Request

from .models import *
from .forms import CreateUserForm
from .decorators import unauthenticated_user
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import vonage





@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            client = vonage.Client(key= '4b2b1283' ,secret='1oyWH3grRTScbiwE')
            email = form.cleaned_data.get('email')
            params = {
                "channel_timeout": 60,
                'brand': 'Events',
                'workflow': [{'channel': 'email', 'to': email}],
            }

            verify_request = client.verify2.new_request(params)
            request.session['request_id'] = verify_request['request_id']
            request.session['form_data'] = form.cleaned_data
            return redirect('otp')

    context = {'form' : form}
    return render(request, 'register.html', context)



@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request,user)
            return redirect('home')

        else:
            messages.info(request, 'Username OR Password is Incorrect')

    context = {}
    return render(request, 'login.html', context)


def otp(request):
    if request.method == 'POST':
        entered_otp = ''.join(request.POST.get(f'otp_{i}','')for i in range(1,5))
        request_id = request.session.get('request_id')
        client = vonage.Client(key= '4b2b1283' ,secret='1oyWH3grRTScbiwE')

        verify_request = client.verify2.check_code(request_id=request_id,code=entered_otp)

        if verify_request['status'] == 'completed':
            form_data = request.session.get('form_data')
            form = CreateUserForm(data=form_data)
            if form.is_valid():
                form.save()
                messages.success(request,'Registeration Completed')
                return redirect('login')


        else:
            request.session['request_id'] = request_id
            messages.error(request,'Invalid OTP')
            return redirect('otp')

    return render(request,'otp.html')

def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url= 'login')
def home(request):
    context= {}
    return render(request, 'home.html', context)