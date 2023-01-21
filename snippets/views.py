from django.shortcuts import render
from django.http import HttpResponse
from snippets.models import Snippet  # Snippet モデルをインポート


# Create your views here.
def top(request):
    snippets = Snippet.objects.all()  # 一覧を取得
    context = {"snippets": snippets}  # テンプレートエンジンに与えるオブジェクト
    return render(request, "snippets/top.html", context)


def snippet_new(request):
    return HttpResponse('スニペットの登録')


def snippet_edit(request, snippet_id):
    return HttpResponse('スニペットの編集')


def snippet_detail(request, snippet_id):
    return HttpResponse('スニペットの詳細閲覧')
