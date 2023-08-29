import bleach
from django import forms
from captcha.fields import CaptchaField
from comments.models import Comment


class CommentForm(forms.ModelForm):

    text_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'accept': 'text/plain'}), required=False)
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    text_preview = forms.CharField(widget=forms.HiddenInput(), required=False)
    captcha = CaptchaField(required=False)  #required=False - костыль

    def clean_text(self):
        cleaned_text = bleach.clean(
            self.cleaned_data['text'],
            tags=['a', 'code', 'i', 'strong'],
            attributes={'a': ['href', 'title']},
            strip=True,
        )
        return cleaned_text

    class Meta:
        model = Comment
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/gif,image/png'}),
        }
