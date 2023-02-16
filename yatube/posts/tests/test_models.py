from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='комментарий к посту'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post_group = {
            PostModelTest.post: PostModelTest.post.text,
            PostModelTest.group: PostModelTest.group.title,
            PostModelTest.comment: PostModelTest.comment.text,
        }
        for key, value in post_group.items():
            with self.subTest(key=key):
                self.assertEqual(value, str(key))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='auth')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_model_follow_have_correct_objects_names(self):
        self.assertTrue(Follow.objects.get(user=self.user, author=self.author))
