from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView

from SPA_comments import settings
from . import tasks
from .forms import CommentForm
from .models import Comment
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template.loader import render_to_string
import bleach
from django.http import JsonResponse


class CustomModelListView(ListView):
    model = Comment
    template_name = 'comments/comment_list.html'
    context_object_name = 'custom_models'

    @method_decorator(cache_page(10))  #кешируем на 10 секунд
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        sort_order = self.request.GET.get('sort', '')
        order_by_field = self.request.GET.get('order_by', 'created_at')

        if order_by_field not in ['user__username', 'email', 'created_at']:
            order_by_field = 'created_at'

        queryset = Comment.objects.filter(parent=None).order_by(order_by_field)

        if sort_order == 'desc':
            queryset = queryset.reverse()

        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)

        return page


class CreateCommentView(View):
    template_name = 'comments/create_comment'

    def get(self, request, *args, **kwargs):
        form = CommentForm()
        return render(request, 'comments/create_comment.html', {'form': form})

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = CommentForm(request.POST, request.FILES)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.email = request.user.email

                if form.cleaned_data['text']:
                    text = form.cleaned_data['text']
                    comment.text = text

                if form.cleaned_data['image']:
                    image = form.cleaned_data['image']
                    processed_image = self.process_image(image)
                    comment.image.save(image.name, processed_image, save=False)

                if form.cleaned_data['text_file']:
                    text_file = form.cleaned_data['text_file']
                    processed_text_file = self.process_text_file(text_file)
                    comment.text_file.save(text_file.name, processed_text_file, save=False)

                comment.save()
                if settings.DEBUG:
                    subject = 'Comment create'
                    text = 'I create comment'
                    email = request.user.email
                    tasks.send_mail.delay(subject, text, email)
                response_data = {
                    'success': True,
                    'message': 'Коментар успішно створено.',
                }
                return JsonResponse(response_data)
            else:
                response_data = {
                    'success': False,
                    'errors': form.errors,
                }
                return JsonResponse(response_data, status=400)

    def process_image(self, image):
        img = Image.open(image)
        max_size = (320, 240)
        img.thumbnail(max_size)

        output_io = BytesIO()
        img.save(output_io, format='JPEG', quality=100)
        output_io.seek(0)

        return InMemoryUploadedFile(
            output_io,
            'ImageField',
            f"{image.name.split('.')[0]}.jpg",
            'image/jpeg',
            output_io.getbuffer().nbytes,
            None
        )

    def process_text_file(self, text_file):
        processed_text = text_file.read()

        if len(processed_text) > 100 * 1024:
            raise ValueError('Розмір файлу повинен бути не більше 100 КБ.')

        return InMemoryUploadedFile(
            BytesIO(processed_text),
            'FileField',
            text_file.name,
            'text/plain',
            len(processed_text),
            None
        )


class ReplyToCommentView(View):
    def get(self, request, parent_id):
        parent_comment = Comment.objects.get(id=parent_id)

        form = CommentForm(initial={'parent': parent_comment})

        return render(request, 'comments/reply_comment.html', {'form': form, 'parent_comment': parent_comment})

    def post(self, request, parent_id):
        parent_comment = Comment.objects.get(id=parent_id)

        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.parent = parent_comment

            if form.cleaned_data['image']:
                image = form.cleaned_data['image']
                processed_image = self.process_image(image)
                comment.image.save(image.name, processed_image, save=False)

            if form.cleaned_data['text_file']:
                text_file = form.cleaned_data['text_file']
                processed_text_file = self.process_text_file(text_file)
                comment.text_file.save(text_file.name, processed_text_file, save=False)

            comment.save()

            return redirect('comment_list')

        return render(request, 'comments/reply_comment.html', {'form': form, 'parent_comment': parent_comment})

    def process_image(self, image):
        img = Image.open(image)
        max_size = (320, 240)
        img.thumbnail(max_size)

        output_io = BytesIO()
        img.save(output_io, format='JPEG', quality=100)
        output_io.seek(0)

        return InMemoryUploadedFile(
            output_io,
            'ImageField',
            f"{image.name.split('.')[0]}.jpg",
            'image/jpeg',
            output_io.getbuffer().nbytes,
            None
        )

    def process_text_file(self, text_file):
        processed_text = text_file.read()

        if len(processed_text) > 100 * 1024:
            raise ValueError('Розмір файлу повинен бути не більше 100 КБ.')

        return InMemoryUploadedFile(
            BytesIO(processed_text),
            'FileField',
            text_file.name,
            'text/plain',
            len(processed_text),
            None
        )


class PreviewCommentView(View):
    def post(self, request):
        text = request.POST.get('text', '')
        cleaned_text = bleach.clean(text, tags=['a', 'code', 'i', 'strong'], strip=True)
        preview_html = render_to_string('comments/comment_preview.html', {'preview': cleaned_text})

        return JsonResponse({'preview': preview_html})
