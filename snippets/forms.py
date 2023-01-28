from django import forms
from django.core.exceptions import ValidationError
from snippets.models import Snippet, Comment

import unicodedata  # unicodedata をインポート


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ('title', 'code', 'description')
        
    def clean_title(self):
        title = self.cleaned_data['title']
        title = unicodedata.normalize('NFKC', title)
        if len(title) < 10:
            raise ValidationError("10文字以上")
        return title


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
