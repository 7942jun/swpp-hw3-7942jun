from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import login, logout, authenticate
from django.forms.models import model_to_dict
from .models import Comment, Article
import json


def signup(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        User.objects.create_user(username=username, password=password)
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['POST'])


@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        from django.contrib.auth.models import User
        return HttpResponseNotAllowed(['GET'])

def signin(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['POST'])

def signout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['GET'])

def article(request):
    if request.method == 'GET':
        article_list = [Article for Article in Article.objects.all().values()]
        return JsonResponse(article_list, safe=False)
    elif request.method == 'POST':
        req_data = json.loads(request.body.decode())
        title = req_data['title']
        content = req_data['content']
        new_article = Article(title=title, content=content, author=request.user)
        new_article.save()
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])        


def article_detail(request, article_id):
    if request.method == 'GET':
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponse(status=404)
        article = model_to_dict(article)
        return JsonResponse(article, safe=False)
    elif request.method == 'PUT':
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponse(status=404)
        req_data = json.loads(request.body.decode())
        title = req_data['title']
        content = req_data['content']
        article.title = title
        article.content = content
        article.save()
        return HttpResponse(status=200)   
    elif request.method == 'DELETE':
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponse(status=404)
        article.delete()
        comments = Comment.objects.filter(article=article_id)
        for comment in comments:
            comment.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['GET', 'POST', 'DELETE'])        
        

def comment(request):
    pass

def comment_detail(reqest):
    pass
