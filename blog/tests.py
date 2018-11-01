from django.test import TestCase, Client
import json


class BlogTestCase(TestCase):
    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Request without csrf token returns 403 response

        response = client.get('/api/token')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signup', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

class ModelTestCase(TestCase):
    def test_models(self):
        from .models import Article, Comment
        from django.contrib.auth.models import User

        new_user = User.objects.create_user(username='swpp', password='iluvswpp')  # Django default user model
        new_article = Article(title='I Love SWPP!', content='Believe it or not', author=new_user)
        new_article.save()
        new_comment = Comment(article=new_article, content='Comment!', author=new_user)
        new_comment.save()

class ArticleTestCase(TestCase):
    def test_article(self):
        from .models import Article, Comment
        from django.contrib.auth.models import User

        new_user = User.objects.create_user(username='swpp', password='iluvswpp')  # Django default user model
        new_article = Article(title='I Love SWPP!', content='Believe it or not', author=new_user)
        new_article.save()
        new_article = Article(title='I Love SWPP2!', content='Believe it or not2', author=new_user)
        new_article.save()
        client = Client()
        response = client.get('/api/article')
        self.assertIn('author_id', response.content.decode())

    def test_article_detail(self):
        
        from .models import Article, Comment
        from django.contrib.auth.models import User
        new_user = User.objects.create_user(username='swpp', password='iluvswpp')  # Django default user model
        new_article = Article(title='First', content='Olleh!', author=new_user)
        new_article.save()
        new_article = Article(title='Second', content='Yeah!', author=new_user)
        new_article.save()
        
        client = Client()
        
        response = client.post('/api/signin', json.dumps({'username':'swpp', 'password':'iluvswpp'}), content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = client.get('/api/article/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('First', response.content.decode())

        response = client.post('/api/article', json.dumps({'title':'Third', 'content':'Wow!'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        response = client.put('/api/article/3', json.dumps({'title':'Third', 'content':'Woo!'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        response = client.get('/api/article/3')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Woo', response.content.decode())
        
        reponse = client.delete('/api/article/3')
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/article/3')
        self.assertEqual(response.status_code, 404)
