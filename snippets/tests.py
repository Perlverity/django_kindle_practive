from django.test import TestCase, Client, RequestFactory
from django.http import HttpRequest
from django.urls import resolve
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from snippets.views import top, snippet_new, snippet_edit, snippet_detail

from snippets.models import Snippet
from snippets.views import top
from .forms import SnippetForm

UserModel = get_user_model()


# Create your tests here.
# トップページがb"HelloWorld"というプレーンテキストではなくHTMLファイルを返すように変更するため、
# #TopPageViewTestクラスは削除して、TopPageTestクラスを次のように書き換え。
class TopPageTest(TestCase):
    def test_top_page_returns_200_and_expected_title(self):
        response = self.client.get('/')
        self.assertContains(response, "Djangoスニペット", status_code=200)

    def test_top_page_uses_expected_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, "snippets/top.html")


class CreateSnippetTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username="test_user",
            email="test@example.com",
            password="secret",
        )
        self.client.force_login(self.user)  # ユーザーログイン

    def test_render_creation_form(self):
        response = self.client.get("/snippets/new")
        self.assertContains(response, "スニペットの登録", status_code=200)

    def test_create_snippets(self):
        data = {'title': 'タイトル', 'code': 'コード', 'description': '解説'}
        self.client.post("/snippets/new", data)
        snippet = Snippet.objects.get(title='タイトル')
        self.assertEqual('コード', snippet.code)
        self.assertEqual('解説', snippet.description)


class SnippetDetailTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username='test_user',
            email='test@example.com',
            password="secret",
        )
        self.snippet = Snippet.objects.create(
            title="タイトル",
            code="コード",
            description="解説",
            created_by=self.user,
        )

    def test_should_user_expected_template(self):
        response = self.client.get("/snippets/%s/" % (self.snippet.id))
        self.assertTemplateUsed(response, "snippets/snippet_detail.html")

    def test_top_page_returns_200_and_expected_heading(self):
        response = self.client.get("/snippets/%s/" % (self.snippet.id))
        self.assertContains(response, self.snippet.title, status_code=200)


class EditSnippetTest(TestCase):
    def test_should_resolve_snippet_edit(self):
        found = resolve("/snippets/1/edit/")
        self.assertEqual(snippet_edit, found.func)


class TopPageRenderSnippetsTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username='test_user',
            email='test@example.com',
            password='top_secret_pass0001',
        )
        self.snippet = Snippet.objects.create(
            title='title1',
            code="print('hello')",
            description='description1',
            created_by=self.user,
        )

    def test_should_return_snippet_title(self):
        request = RequestFactory().get('/')
        request.user = self.user
        response = top(request)
        self.assertContains(response, self.snippet.title)

    def test_should_return_username(self):
        request = RequestFactory().get('/')
        request.user = self.user
        response = top(request)
        self.assertContains(response, self.user.username)


class SnippetFormTests(TestCase):
    def test_valid_when_given_long_title(self):
        params = {
            'title': '1234567891234',
            'code': 'print("Hello World")',
            'description': 'ただ表示するだけ',
            }
        snippet = Snippet()
        form = SnippetForm(params, instance=snippet)
        self.assertTrue(form.is_valid())

    def test_invalid_when_given_too_short_title(self):
        params = {
            'title': '012345678',
            'code': 'print("Hello World")',
            'description': 'ただ表示するだけ',
            }
        snippet = Snippet()
        form = SnippetForm(params, instance=snippet)
        self.assertFalse(form.is_valid())

    def test_normalize_unicode_data(self):
        params = {
            'title': '"Hｈ"のようなUnicode',
            'code': 'print("Hello World")',
            'description': 'ただ表示するだけ',
            }
        snippet = Snippet()
        form = SnippetForm(params, instance=snippet)
        form.is_valid()

        actual = form.cleaned_data['title']
        expected = '"Hh"のようなUnicode'
        self.assertEqual(expected, actual)


class SnippetCreateViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserModel.objects.create_user(username='c-bata', email='suganuma@example.com', password='secret')

    def test_should_return_200_if_sending_get_request(self):
        request = self.factory.get("/endpoint/of/create_snippet")
        request.user = self.user
        response = snippet_new(request)
        self.assertEqual(200, response.status_code)

    def test_should_redirect_200_if_user_does_not_login(self):
        request = self.factory.get("/endpoint/of/create_snippet")
        request.user = AnonymousUser()
        response = snippet_new(request)
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_should_return_400_if_sending_empty_post_request(self):
        request = self.factory.get("/endpoint/of/create_snippet", data={})
        request.user = self.user
        response = snippet_new(request)
        self.assertEqual(400, response.status_code)

    def test_should_return_200_if_sending_valid_post_request(self):
        request = self.factory.get("/endpoint/of/create_snippet", data={
            'title': '1234567891234',
            'code': 'print("Hello World")',
            'description': 'ただ表示するだけ',
        })
        request.user = self.user
        response = snippet_new(request)
        self.assertEqual(200, response.status_code)