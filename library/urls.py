from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet, BorrowRecordViewSet, generate_report_view, latest_report_view 

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register(r'borrow', BorrowRecordViewSet, basename='borrowrecord')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/', generate_report_view, name='generate-report'),
    path('reports/latest/', latest_report_view, name='latest-report'),
    # path('borrow/', borrow_book, name='borrow-book'),
    # path('return/<int:record_id>/', return_book, name='borrow-record-return-book'),
    # path('borrowrecord/return/<int:pk>/', ReturnBookView.as_view(), name='borrowrecord-return-book'),

]
