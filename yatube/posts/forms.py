from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Введите текст', 'group': 'Выберите группу'}

    def clean_text(self):
        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError('Заполните поле')
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
