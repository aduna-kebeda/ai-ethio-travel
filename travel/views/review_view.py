from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from ..models.review import Review, ReviewImage, ReviewLike
from ..serializers import (
    ReviewSerializer, ReviewCreateSerializer,
    ReviewImageSerializer, ReviewLikeSerializer,
    ReviewUpdateSerializer
)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['destination', 'rating']
    search_fields = ['content']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return Review.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        review = self.get_object()
        like, created = ReviewLike.objects.get_or_create(
            user=request.user,
            review=review
        )
        if not created:
            like.delete()
            return Response({'message': 'Like removed.'}, status=status.HTTP_200_OK)
        serializer = ReviewLikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        review = self.get_object()
        likes = ReviewLike.objects.filter(review=review)
        serializer = ReviewLikeSerializer(likes, many=True)
        return Response(serializer.data)

class ReviewImageViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReviewImage.objects.filter(review__user=self.request.user)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_pk'])
        if review.user != self.request.user:
            return Response(
                {'error': 'You can only add images to your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(review=review)

class ReviewLikeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReviewLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ReviewLike.objects.all()
        return ReviewLike.objects.filter(user=self.request.user)
    