from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from captcha.models import CaptchaStore
from .models import Comment


def get_captcha():
    """Хелпер: створює капчу і повертає key + value для тестів."""
    CaptchaStore.generate_key()
    captcha = CaptchaStore.objects.latest('pk')
    return captcha.hashkey, captcha.response


class CommentModelTest(TestCase):
    """Тести моделі Comment."""

    def test_str_representation(self):
        comment = Comment.objects.create(
            user_name='TestUser',
            email='test@example.com',
            text='Hello world',
        )
        self.assertIn('TestUser', str(comment))

    def test_homepage_blank_by_default(self):
        comment = Comment.objects.create(
            user_name='TestUser',
            email='test@example.com',
            text='Hello',
        )
        self.assertEqual(comment.homepage, '')

    def test_reply_has_parent(self):
        parent = Comment.objects.create(
            user_name='Parent',
            email='parent@example.com',
            text='Parent comment',
        )
        reply = Comment.objects.create(
            user_name='Child',
            email='child@example.com',
            text='Reply',
            parent=parent,
        )
        self.assertEqual(reply.parent, parent)
        self.assertIn(reply, parent.replies.all())


class CommentAPITest(TestCase):
    """Тести REST API."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('comment-list')

    def test_get_comments_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_comments_has_pagination(self):
        response = self.client.get(self.url)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_create_comment_success(self):
        key, value = get_captcha()
        response = self.client.post(self.url, {
            'user_name': 'TestUser',
            'email': 'test@example.com',
            'text': 'Hello world',
            'captcha_key': key,
            'captcha_value': value,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_comment_invalid_username(self):
        key, value = get_captcha()
        response = self.client.post(self.url, {
            'user_name': 'Test User!',  # пробіл і ! — заборонені
            'email': 'test@example.com',
            'text': 'Hello',
            'captcha_key': key,
            'captcha_value': value,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('user_name', response.data)

    def test_create_comment_wrong_captcha(self):
        key, _ = get_captcha()
        response = self.client.post(self.url, {
            'user_name': 'TestUser',
            'email': 'test@example.com',
            'text': 'Hello',
            'captcha_key': key,
            'captcha_value': 'wrongvalue',
        })
        self.assertEqual(response.status_code, 400)

    def test_create_comment_missing_required_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)

    def test_ordering_by_created_at(self):
        # Створюємо два коментарі
        key1, val1 = get_captcha()
        self.client.post(self.url, {
            'user_name': 'First',
            'email': 'first@example.com',
            'text': 'First comment',
            'captcha_key': key1,
            'captcha_value': val1,
        })
        key2, val2 = get_captcha()
        self.client.post(self.url, {
            'user_name': 'Second',
            'email': 'second@example.com',
            'text': 'Second comment',
            'captcha_key': key2,
            'captcha_value': val2,
        })
        # LIFO — другий має бути першим
        response = self.client.get(self.url)
        results = response.data['results']
        self.assertEqual(results[0]['user_name'], 'Second')