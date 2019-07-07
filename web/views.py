from django.shortcuts import render
from json import JSONEncoder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.models import Token,Income,Expense,User,Passwordresetcodes
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.conf import settings
from postmark import PMMail
import requests

# Create your views here.

random_str = lambda N: ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digit) for i in range(N))


@csrf_exempt
def register(request):
    if 'requestcode' in request.POST:
        if not grecaptcha_verify(request):
            context = {'message':'کد اشتباه'}
            return render(request,'register.html',context)
        if User.objects.filter(email = request.POST['email']).exists():
            context = {'message':'user exists'}
            return render(request,'register.html',context)
        if not User.objects.filter(username = request.POST['username']).exists():
            code = random_str(28)
            now = datetime.now()
            email = request.POST['email']
            password = request.POST['password']
            username = request.POST['username']
            temporarycode = Passwordresetcodes(email = email,time = now,code = code,username = username,password = password)
            temporarycode.save()
            message = PMMail(api_key = settings.POSTMARK_API_TOKEN,
                subject = "فعال سازی اکانت",
                sender = "fahim.kammand2@gmail.com",
                to = email,
                text_body = "for active click on it: https://bestoon.ir/accounts/register/?email={}&code={}".format(email,code),
                tag = "account request")
            message.send()
            context = {'message':'activate link sent'}
            return render(request,'login.html',context)
        else:
            context = {'message' : 'temporary username'}
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
