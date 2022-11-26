from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:group_list", kwargs={"slug": "test_slug"}):
                "posts/group_list.html",
            reverse("posts:profile", kwargs={"username": "auth"}):
                "posts/profile.html",
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}):
                "posts/post_detail.html",
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}):
                "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон posts:index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))

        self.assertEqual(
            response.context["page_obj"][0].author.username,
            self.post.author.username,
        )
        self.assertEqual(
            response.context["page_obj"][0].text,
            self.post.text,
        )
        self.assertEqual(
            response.context["page_obj"][0].group.title, self.post.group.title
        )

    def test_group_posts_page_show_correct_context(self):
        """Шаблон posts:group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        object_list = response.context['page_obj'].object_list
        expected_posts = list(self.group.posts.all()[:10])
        self.assertListEqual(expected_posts, object_list)

        self.assertEqual(
            response.context["page_obj"].object_list[0].author.username,
            self.post.author.username,
        )
        self.assertEqual(
            response.context["page_obj"].object_list[0].text,
            self.post.text,
        )
        self.assertEqual(
            response.context["page_obj"].object_list[0].group.title,
            self.post.group.title,
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон posts:profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={"username": self.post.author.username},
            )
        )
        object_list = response.context['page_obj'].object_list
        expected_posts = list(self.group.posts.all()[:10])
        self.assertListEqual(expected_posts, object_list)

        self.assertEqual(
            response.context["page_obj"].object_list[0].author.username,
            self.post.author.username,
        )
        self.assertEqual(
            response.context["page_obj"].object_list[0].text,
            self.post.text,
        )
        self.assertEqual(
            response.context["page_obj"].object_list[0].group.title,
            self.post.group.title,
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон posts:post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={"post_id": self.post.id},
            )
        )
        self.assertEqual(
            response.context["post"].author.username,
            self.post.author.username,
        )
        self.assertEqual(
            response.context["post"].text,
            self.post.text,
        )
        self.assertEqual(
            response.context["post"].group.title,
            self.post.group.title,
        )

    def test_post_create_page_show_correct_context(self):
        """Шаблон posts:post_create  сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_create',
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон posts:post_edit  сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={"post_id": self.post.id},
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )

        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'0123456789012345Тестовый пост{str(i)}',
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "test_slug"}),
            reverse("posts:profile", kwargs={"username": "auth"}),
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        templates_pages_names = {
            reverse("posts:index") + '?page=2',
            reverse("posts:group_list", kwargs={"slug": "test_slug"})
            + '?page=2',
            reverse("posts:profile", kwargs={"username": "auth"}) + '?page=2',
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 3)


class CreateNewPostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username="auth1")
        cls.user2 = User.objects.create_user(username="auth2")
        cls.group1 = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.group2 = Group.objects.create(
            title="Тестовая группа2",
            slug="test_slug2",
            description="Тестовое описание2",
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Тестовый пост1',
            group=cls.group1,
        )
        cls.post2 = Post.objects.create(
            author=cls.user2,
            text='Тестовый пост2',
            group=cls.group2,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_post2_in_index_group2_list_profile(self):
        templates_pages_names = {
            reverse("posts:index"),
            reverse(
                "posts:group_list", kwargs={"slug": self.post2.group.slug}
            ),
            reverse(
                "posts:profile",
                kwargs={"username": self.post2.author.username},
            ),
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertIn(self.post2, response.context['page_obj'])

    def test_post2_not_in_group1_list(self):
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.post1.group.slug})
        )
        self.assertNotIn(self.post2, response.context['page_obj'])
