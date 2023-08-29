from django.urls import path

from comments.views import CustomModelListView, CreateCommentView, ReplyToCommentView, PreviewCommentView

urlpatterns = [
    path('', CustomModelListView.as_view(), name='comment_list'),
    path('create/', CreateCommentView.as_view(), name='create_comment'),
    path('reply/<int:parent_id>', ReplyToCommentView.as_view(), name='reply_to_comment'),
    path('preview_comment/', PreviewCommentView.as_view(), name='preview_comment'),

]
