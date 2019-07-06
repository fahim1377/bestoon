from django.shortcuts import render
from json import JSONEncoder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.models import Token,Income,Expense,User
from datetime import datetime
# Create your views here.
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
