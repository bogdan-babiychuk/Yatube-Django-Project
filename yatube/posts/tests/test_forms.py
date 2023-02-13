from http import HTTPStatus
from django.shortcuts import get_object_or_404
from posts.models import Post, Group, User, Comment
from django.test import Client, TestCase
from django.urls import reverse


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='wtf')

        cls.group = Group.objects.create(
            title='test-группа',
            slug='test-slug',
            description='test-описание группы'
        )
        cls.group_new = Group.objects.create(
            title='Заголовок_новый',
            slug='test_slug_new',
            description='текстовоеполедлянаборатекста'
        )
        cls.post = Post.objects.create(
            text='text-текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'text-текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     args=[get_object_or_404(User,
                                                             username='wtf')]))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='text-текст',
            ).exists()
        )

    def test_cant_create_existing_slug(self):
        # Подсчитаем количество записей в Task
        tasks_count = Post.objects.count()
        form_data = {
            'title': 'Заголовок из формы',
            'text': 'Текст из формы',
            'group': self.group,
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Проверка формы редактирования поста"""
        form_data = {
            'text': 'Тестовый тест 2',
            'group': self.group_new.id
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            ))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый тест 2',
                group=self.group_new.id
            ).exists())
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group.id
            ).exists())


class CommentTest(TestCase):
    def test_comment(self):
        self.user = User.objects.create_user(username='wtf')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='test-группа',
            slug='test-slug',
            description='test-описание группы')

        self.post = Post.objects.create(
            text='text-текст',
            author=self.user,
            group=self.group,
        )
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='Текст коммента'
        )

        comment_count = Comment.objects.count()
        form_data = {'text': comment}
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      self.post.id}),
                                              data=form_data,
                                              folow=True)
        new_comment = Comment.objects.get(id=self.post.id)
        self.assertContains(response, 'Текст коммента')
        values = {
            comment.text: new_comment.text,
            self.user: new_comment.author
        }
        for value, value_comment in values.items():
            with self.subTest(value=value):
                self.assertEqual(value, value_comment)
        self.assertEqual(Comment.objects.count(), comment_count)
