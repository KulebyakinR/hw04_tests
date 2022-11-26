
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data)
        self.assertEqual(
            Post.objects.latest('pub_date').text, form_data['text']
        )
        Post.objects.latest('pub_date').text
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_form(self):
        """Проверка измения записи в БД при редактировании поста"""
        self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        post_new_data = {
            'text': 'Другой текст поста',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ), data=post_new_data
        )
        self.assertTrue(Post.objects.filter(
            text=post_new_data['text'],
            group=post_new_data['group'],
        ).exists()
        )
