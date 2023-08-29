from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from comment_api.serializers import CommentSerializer, UserSerializer
from comments.models import Comment
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


class CreateUserAPIView(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreateAPIView(APIView):
    def get(self, request, format=None):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(user=self.request.user)

            image = request.data.get('image')
            if image:
                processed_image = self.process_image(image)
                comment.image.save(image.name, processed_image, save=True)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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