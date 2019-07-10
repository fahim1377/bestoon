from django.shortcuts import render
from json import JSONEncoder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.models import Token,Income,Expense,User,Passwordresetcodes
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.conf import settings
from postmark import PMMail
from django.core.mail import send_mail
import requests
import random
import string
import time

# Create your views here.

random_str = lambda N: ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits) for i in range(N))




def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def grecaptcha_verify(request):
    if request.method == 'POST':
        data = request.POST
        captcha_rs = data.get('g-recaptcha-response')
        url = "https://www.google.com/recaptcha/api/siteverify"
        params = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': captcha_rs,
            'remoteip': get_client_ip(request)
        }
        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()
        return verify_rs.get("success",False)

@csrf_exempt
def register(request):


    if 'requestcode' in request.POST:
        if not grecaptcha_verify(request):
            context = {'message':'کد اشتباه'}
            return render(request,'register.html',context)
        """return JsonResponse({
        'status': request.POST['code']
        },encoder = JSONEncoder)
        """
        if User.objects.filter(email = request.POST['email']).exists():
            context = {'message':'user exists'}
            """return JsonResponse({
            'status': request.POST['code']
            },encoder = JSONEncoder)
            """
            return render(request,'register.html',context)
        if not User.objects.filter(username = request.POST['username']).exists():
            code = random_str(28)
            now = datetime.now()
            email = request.POST['email']
            password = request.POST['password']
            username = request.POST['username']
            temporarycode = Passwordresetcodes(email = email,time = now,code = code,username = username,password = password)
            temporarycode.save()
            text_body = "for active click on it: http://localhost:8009/register/?email={}&code={}".format(email,code)

            """
            return JsonResponse({
            'status': request.POST['code']
            },encoder = JSONEncoder)
            """

            subject = 'Thank you for registering to our site'
            message = ' it  means a world to us '
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail( subject, text_body, email_from,recipient_list,fail_silently=False )

            """
            return JsonResponse({
            'status': request.POST['code']
            },encoder = JSONEncoder)
            """
            context = {'message':'activate link sent'}
            return render(request,'login.html',context)
        else:
            context = {'message' : 'temporary username'}
            """return JsonResponse({
            'status': request.POST['code']
            },encoder = JSONEncoder)"""
            return render(request,'register.html',context)
    elif 'code' in request.GET:
        email = request.GET['email']
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(code = code).exists():
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            new_user = User.objects.create(username = new_temp_user.username,password = new_temp_user.password,email = email)
            this_token = random_str(48)
            token = Token.objects.create(token = this_token,user = new_user)
            Passwordresetcodes.objects.filter(code=code).delete()
            context = {'message':'your account is activated'}
            return render(request,'login.html',context)
        else:
            context = {'message':'code is invalid'}
            return render(request,'register.html',context)
    else:
        context = {'message':''}
        return render(request,'register.html',context)


@csrf_exempt
def login(request):
    if 'requestcode' in request.POST:
        if not grecaptcha_verify(request):
            context = {'message':'کد اشتباه'}
            return render(request,'register.html',context)
        """return JsonResponse({
        'status': request.POST['code']
        },encoder = JSONEncoder)
        """
        if User.objects.filter(email = request.POST['email']).exists():
            context = {'message':'user exists'}
            """return JsonResponse({
            'status': request.POST['code']
            },encoder = JSONEncoder)
            """
            return render(request,'register.html',context)
        if not User.objects.filter(username = request.POST['username']).exists():
            code = random_str(28)
            now = datetime.now()
            email = request.POST['email']
            password = request.POST['password']
            username = request.POST['username']
            temporarycode = Passwordresetcodes(email = email,time = now,code = code,username = username,password = password)
            temporarycode.save()
            text_body = "for active click on it: {}?email={}&code={}".format(request.build_absolute_uri('/register/'),email,code)

            """
            return JsonResponse({
            'status': request.POST['code']
            },encoder = JSONEncoder)
            """

            subject = 'Thank you for registering to our site'
            message = ' it  means a world to us '
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail( subject, text_body, email_from,recipient_list,fail_silently=False )

            """
            return JsonResponse({
            'status': request.POST['code']
            },encoder = JSONEncoder)
            """
            context = {'message':'activate link sent'}
            return render(request,'login.html',context)
        else:
            context = {'message' : 'temporary username'}
            """return JsonResponse({
            'status': request.POST['code']
            },encoder = JSONEncoder)"""
            return render(request,'register.html',context)
    elif 'code' in request.GET:
        email = request.GET['email']
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(code = code).exists():
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            new_user = User.objects.create(username = new_temp_user.username,password = new_temp_user.password,email = email)
            this_token = random_str(48)
            token = Token.objects.create(token = this_token,user = new_user)
            Passwordresetcodes.objects.filter(code=code).delete()
            context = {'message':'your account is activated'}
            return render(request,'login.html',context)
        else:
            context = {'message':'code is invalid'}
            return render(request,'register.html',context)
    else:
        context = {'message':''}
        return render(request,'login.html',context)









@csrf_exempt
def submit_expense(request):
    """user submits an expense"""
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token = this_token).get()
    now = datetime.now()
    Expense.objects.create(user = this_user,amount = request.POST['amount'],text = request.POST['text'],date = now)

    return JsonResponse({
        'status':'ok'
    },encoder = JSONEncoder)



@csrf_exempt
def submit_income(request):
    """user submits an income"""
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token = this_token).get()
    now = datetime.now()
    amount = request.POST['amount']
    text = request.POST['text']
    Income.objects.create(user = this_user,amount = amount,text = text,date = now)

    return JsonResponse({
        'status':'ok'
    },encoder = JSONEncoder)
