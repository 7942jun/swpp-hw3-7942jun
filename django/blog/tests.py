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
        self.assertEqual(response.status_code, 204)
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signup', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection
      
        response = client.delete('/api/signup', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        response = client.delete('/api/token', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

class ModelTestCase(TestCase):
    def test_models(self):
        from .models import Article, Comment
        from django.contrib.auth.models import User

        new_user = User.objects.create_user(username='swpp', password='iluvswpp')  # Django default user model
        new_article = Article(title='I Love SWPP!', content='Believe it or not', author=new_user)
        new_article.save()
        new_comment = Comment(article=new_article, content='Comment!', author=new_user)
        new_comment.save()

class SignTestCase(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        new_user = User.objects.create_user(username='swpp', password='iluvswpp')
        new_user = User.objects.create_user(username='jun', password='1234')

    def test_signinout(self):
        client = Client()
        response = client.post('/api/signin', json.dumps({'username':'swpp', 'password':'iluvswpp'}), content_type='application/json')
        self.assertEqual(response.status_code, 204)
        
        response = client.get('/api/signout')
        self.assertEqual(response.status_code, 204)

        response = client.get('/api/signout')
        self.assertEqual(response.status_code, 401)

        response = client.post('/api/signin', json.dumps({'username':'swppp', 'password':'iluvswpp'}), content_type='application/json')
        self.assertEqual(response.status_code, 401)

        response = client.put('/api/signin', json.dumps({'username':'swpp', 'password':'iluvswpp'}), content_type='application/json')
        self.assertEqual(response.status_code, 405)

        response = client.delete('/api/signin')
        self.assertEqual(response.status_code, 405)

        response = client.get('/api/signin')
        self.assertEqual(response.status_code, 405)

        response = client.post('/api/signout', json.dumps({'username':'swppp', 'password':'iluvswpp'}), content_type='application/json')
        self.assertEqual(response.status_code, 405)
        
        response = client.put('/api/signout', json.dumps({'username':'swpp', 'password':'iluvswpp'}), content_type='application/json')
        self.assertEqual(response.status_code, 405)

        response = client.delete('/api/signout')
        self.assertEqual(response.status_code, 405)

class ArticleTestCase(TestCase):
    def setUp(self):
        from .models import Article, Comment
        from django.contrib.auth.models import User
        new_user = User.objects.create_user(username='swpp', password='iluvswpp')  # Django default user model
        second_user = User.objects.create_user(username='jun', password='7942')  # Django default user model
        article1 = Article(title='First', content='11111', author=new_user)
        article1.save()
        article2 = Article(title='Second', content='22222', author=new_user)
        article2.save()
        article3 = Article(title='Third', content='33333', author=second_user)
        article3.save()
        comment1 = Comment(article=article3, content='1', author=second_user)
        comment1.save()

    def test_article(self):
        client = Client()
        
        response = client.get('/api/article')
        self.assertEqual(response.status_code, 401)
        
        response = client.post('/api/article', json.dumps({'title':'Fourth', 'content':'44444'}), content_type='application/json')
        self.assertEqual(response.status_code, 401)

        client.post('/api/signin', json.dumps({'username':'jun', 'password':'7942'}), content_type='application/json')
        
        response = client.get('/api/article')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(json.loads(response.content.decode())))

        response = client.post('/api/article', json.dumps({'title':'Fourth', 'content':'44444'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/article')
        self.assertEqual(4, len(json.loads(response.content.decode())))

        response = client.delete('/api/article')
        self.assertEqual(response.status_code, 405)

    def test_article_detail(self):
        client = Client()

        response = client.get('/api/article/3')
        self.assertEqual(response.status_code, 401)

        response = client.put('/api/article/4')
        self.assertEqual(response.status_code, 401)

        response = client.delete('/api/article/4')
        self.assertEqual(response.status_code, 401)

        client.post('/api/signin', json.dumps({'username':'jun', 'password':'7942'}), content_type='application/json')        

        response = client.get('/api/article/4')
        self.assertEqual(response.status_code, 404)

        response = client.get('/api/article/3')
        self.assertEqual(response.status_code, 200)
        self.assertIn('33333', response.content.decode())

        response = client.put('/api/article/3', json.dumps({'title':'Third', 'content':'31313'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = client.get('/api/article/3')
        self.assertIn('31313', response.content.decode())
        
        response = client.put('/api/article/4', json.dumps({'title':'Third', 'content':'31313'}), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        response = client.put('/api/article/2', json.dumps({'title':'Third', 'content':'31313'}), content_type='application/json')
        self.assertEqual(response.status_code, 403)

        response = client.delete('/api/article/3')
        self.assertEqual(response.status_code, 200)
        response = client.get('/api/article/3')
        self.assertEqual(response.status_code, 404)

        response = client.get('/api/comment/1')
        self.assertEqual(response.status_code, 404)
    
        response = client.delete('/api/article/3')
        self.assertEqual(response.status_code, 404)
        response = client.delete('/api/article/2')
        self.assertEqual(response.status_code, 403)

        response = client.post('/api/article/1')
        self.assertEqual(response.status_code, 405)

class CommentTestCase(TestCase):
    def setUp(self):
        from .models import Article, Comment
       	from django.contrib.auth.models import User
        new_user = User.objects.create_user(username='swpp', password='iluvswpp')  # Django default user model
        second_user = User.objects.create_user(username='jun', password='7942')  # Django default user model
        article1 = Article(title='First', content='11111', author=new_user)
        article1.save()
        article2 = Article(title='Second', content='22222', author=new_user)
        article2.save()
        article3 = Article(title='Third', content='33333', author=second_user)
        article3.save()
        comment1 = Comment(article=article1, content='c1', author=new_user)
        comment1.save()
        comment2 = Comment(article=article1, content='c2', author=new_user)
        comment2.save()
        comment3 = Comment(article=article3, content='c3', author=second_user)
        comment3.save()

    def test_comment(self):
        client = Client()
        
        response = client.get('/api/article/1/comment')
        self.assertEqual(response.status_code, 401)

        response = client.post('/api/article/1/comment')
        self.assertEqual(response.status_code, 401)

        client.post('/api/signin', json.dumps({'username':'jun', 'password':'7942'}), content_type='application/json')
        
        response = client.get('/api/article/1/comment')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(json.loads(response.content.decode())))

        response = client.post('/api/article/1/comment', json.dumps({'content':'c4'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/article/1/comment')
        self.assertEqual(3, len(json.loads(response.content.decode())))

        response = client.delete('/api/article/1/comment')
        self.assertEqual(response.status_code, 405)

        response = client.put('/api/article/1/comment')
        self.assertEqual(response.status_code, 405)

    def test_comment_detail(self):
        client = Client()

        response = client.get('/api/comment/3')
        self.assertEqual(response.status_code, 401)

        response = client.delete('/api/comment/4')
        self.assertEqual(response.status_code, 401)
        
        response = client.put('/api/comment/4')
        self.assertEqual(response.status_code, 401)

        client.post('/api/signin', json.dumps({'username':'jun', 'password':'7942'}), content_type='application/json')        

        response = client.get('/api/comment/4')
        self.assertEqual(response.status_code, 404)

        response = client.get('/api/comment/3')
        self.assertEqual(response.status_code, 200)
        self.assertIn('c3', response.content.decode())

        response = client.put('/api/comment/3', json.dumps({'content':'31313'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = client.get('/api/comment/3')
        self.assertIn('31313', response.content.decode())
        
        response = client.put('/api/comment/2', json.dumps({'content':'31313'}), content_type='application/json')
        self.assertEqual(response.status_code, 403)
       
        response = client.put('/api/comment/4', json.dumps({'content':'31313'}), content_type='application/json')
        self.assertEqual(response.status_code, 404)

        response = client.delete('/api/comment/3')
        self.assertEqual(response.status_code, 200)
        response = client.get('/api/comment/3')
        self.assertEqual(response.status_code, 404)
        
        response = client.delete('/api/comment/3')
        self.assertEqual(response.status_code, 404)
        
        response = client.delete('/api/comment/2')
        self.assertEqual(response.status_code, 403)
        
        response = client.post('/api/comment/3', json.dumps({'content':'111'}), content_type='application/json')
        self.assertEqual(response.status_code, 405)
        
        response = client.put('/api/comment/3', json.dumps({'content':'111'}), content_type='application/json')
        self.assertEqual(response.status_code, 404)
