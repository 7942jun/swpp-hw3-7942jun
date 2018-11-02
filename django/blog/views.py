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
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        article_list = [Article for Article in Article.objects.all().values('title', 'content', 'author')]
        return JsonResponse(article_list, safe=False)
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
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
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponse(status=404)
        article = model_to_dict(article, fields={'title', 'content', 'author'})
        return JsonResponse(article, safe=False)
    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponse(status=404)
        if article.author.id != request.user.id:
            return HttpResponse(status=403)
        req_data = json.loads(request.body.decode())
        title = req_data['title']
        content = req_data['content']
        article.title = title
        article.content = content
        article.save()
        return HttpResponse(status=200)   
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponse(status=404)
        if article.author.id != request.user.id:
            return HttpResponse(status=403)
        article.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['GET', 'POST', 'DELETE'])        
        

def comment(request, article_id):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        comment_list = [Comment for Comment in Comment.objects.filter(article=article_id).values('article', 'content', 'author')]
        return JsonResponse(comment_list, safe=False)
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        req_data = json.loads(request.body.decode())
        content = req_data['content']
        new_comment = Comment(article=Article.objects.get(id=article_id), content=content, author=request.user)
        new_comment.save()
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['GET', 'POST']) 

def comment_detail(request, comment_id):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponse(status=404)
        comment = model_to_dict(comment, fields={'article', 'content', 'author'})
        return JsonResponse(comment, safe=False)
    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponse(status=404)
        if comment.author.id != request.user.id:
            return HttpResponse(status=403)
        req_data = json.loads(request.body.decode())
        content = req_data['content']
        comment.content = content
        comment.save()
        return HttpResponse(status=200)
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponse(status=404)
        if comment.author.id != request.user.id:
            return HttpResponse(status=403)
        comment.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])




