from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='wtf')

        cls.group = Group.objects.create(
            title='test-Группа',
            slug='test-slug',
            description='test-описание группы'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.url_public = [
            '/',
            '/group/test-slug/',
            '/posts/1/',
            '/profile/wtf/',
        ]
        cls.url_private = [
            '/posts/1/edit'
        ]

        cls.url_authorized = [
            '/',
            '/group/test-slug/',
            '/posts/1/',
            '/profile/wtf/',
            '/create/',
            '/follow/'
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_detail_url_exists_at_desired_location(self):
        """проверка доступности страниц любому пользователю."""

        for url in self.url_public:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_detail_url_exists_at_desired_location_authorized(self):
        """проверка доступности страниц авторизованному пользователю тоже."""

        for url in self.url_authorized:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_url_exists_for_author(self):
        """проверка доступности страниц только автору."""
        for url in self.url_private:
            with self.subTest(url=url):
                post_user = get_object_or_404(User, username='wtf')
                if post_user == self.authorized_client:
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/wtf/',
            'posts/post_edit.html': '/posts/1/edit/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/create/',
            'posts/follow.html': '/follow/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
