from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
SHORT_WORD = 15


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Group name'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Group slug'
    )
    description = models.TextField(
        verbose_name='Group description'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='get_posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Group',
        related_name='group_list'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:SHORT_WORD]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    text = models.TextField(
        max_length=200,
    )

    created = models.DateTimeField(
        verbose_name='Дата коммента',
        auto_now_add=True,
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )   
