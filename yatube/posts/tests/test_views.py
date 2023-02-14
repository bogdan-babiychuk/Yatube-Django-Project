import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='wtf')

        cls.group = Group.objects.create(
            title='test-группа',
            slug='test-slug',
            description='test-описание группы'
        )
        cls.post = Post.objects.create(
            text='text-текст',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': (reverse('posts:index')),
            'posts/group_list.html': (reverse('posts:group_posts',
                                      kwargs={'slug': 'test-slug'})),
            'posts/profile.html': reverse(
                'posts:profile',
                args=[get_object_or_404(User, username='wtf')]),
            'posts/post_detail.html': (reverse('posts:post_detail',
                                       kwargs={'post_id': self.post.pk})),
            'posts/post_edit.html':
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        post_object = response.context['page_obj'][0]
        author = post_object.author
        text = post_object.text
        group = post_object.group
        self.assertEqual(author, self.user)
        self.assertEqual(text, self.post.text)
        self.assertEqual(group, self.post.group)

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_posts',
                                                 kwargs={'slug': 'test-slug'}))
        self.assertIn('group', response.context)
        post_object = response.context['group']
        title = post_object.title
        slug = post_object.slug
        description = post_object.description
        self.assertEqual(title, self.group.title)
        self.assertEqual(slug, self.group.slug)
        self.assertEqual(description, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': 'wtf'}))
        self.assertEqual(response.context['page_obj'][0].author.username,
                         'wtf')
        self.assertEqual(response.context['page_obj'][0].text,
                         'text-текст')
        self.assertEqual(response.context['page_obj'][0].group.title,
                         'test-группа')
        self.assertEqual(response.context['author'],
                         self.user)

    def test_post_detail_page_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(response.context['post'], self.post)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id':
                                                              self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='wtf')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title='test-группа',
            slug='test-slug',
            description='test-описание группы'
        )

        bilk_post: list = []
        for i in range(13):
            bilk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bilk_post)

    def test_first_page_index_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_posts_contains_ten_records(self):
        response = self.client.get(reverse('posts:group_posts',
                                           kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_posts_contains_three_records(self):
        response = self.client.get(reverse('posts:group_posts',
                                           kwargs={'slug':
                                                   'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            args=[get_object_or_404(User,
                                    username='wtf')]))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            args=[get_object_or_404(User,
                                    username='wtf')]) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageExsitsContext(TestCase):
    @classmethod
    def setUpclass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Bogdan')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='Bogdan')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

        self.group = Group.objects.create(
            title='test-группа',
            slug='test-slug',
            description='test-описание группы'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='text-текст',
            group=self.group,
            image=self.uploaded,
        )

    def test_urls_have_img(self):
        urls = {
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'wtf'}),
        }

        for page in urls:
            with self.subTest(post=page):
                response = self.guest_client.get(page)
        img = response.context['page_obj'][0].image.name
        self.assertEqual(self.post.image.name, img)

    def test_post_detail_have_img(self):

        response_for_detail = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        img_for_detail = response_for_detail.context['post'].image.name
        self.assertIn(self.post.image.name, img_for_detail)
