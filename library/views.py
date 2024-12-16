from datetime import datetime
from pathlib import Path
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Author, Book, BorrowRecord
from .serializers import AuthorSerializer, BookSerializer, BorrowRecordSerializer
from .tasks import generate_report
import os
import json
from django.http import JsonResponse


# ViewSet for managing authors
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        # Handle case when no authors exist
        try:
            return Author.objects.all()
        except Exception as e:
            raise Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ViewSet for managing books
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        # Handle case when no books exist
        try:
            return Book.objects.all()
        except Exception as e:
            raise Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ViewSet for managing borrow records
class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer

    @action(detail=True, methods=['put'])
    def return_book(self, request, pk=None):
        try:
            record = self.get_object()
            
            # Check if the record exists and is borrowed
            if not record.return_date:
                record.return_date = datetime.now()
                record.book.available_copies += 1  # Increment available copies by 1
                record.book.save()  # Save the book with updated available copies
                record.save()  # Save the borrow record with updated return date

                return Response({'message': 'Book returned successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Book already returned'}, status=status.HTTP_400_BAD_REQUEST)
        except BorrowRecord.DoesNotExist:
            return Response({'error': 'Borrow record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def borrow_book(self, request):
        try:
            book_id = request.data.get('book_id')
            borrowed_by = request.data.get('borrowed_by')

            if not book_id or not borrowed_by:
                return Response({"error": "Book ID and Borrower Name are required"}, status=status.HTTP_400_BAD_REQUEST)

            book = get_object_or_404(Book, id=book_id)

            # Check if there are available copies
            if book.available_copies > 0:
                borrow_record = BorrowRecord.objects.create(
                    book=book,
                    borrowed_by=borrowed_by,
                    borrow_date=datetime.now(),
                )
                book.available_copies -= 1  # Decrease available copies by 1
                book.save()  # Save the book with updated available copies

                return Response({
                    'message': 'Book borrowed successfully',
                    'borrow_record': BorrowRecordSerializer(borrow_record).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'No available copies'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# API View to trigger report generation using Celery
@api_view(['POST'])
def generate_report_view(request):
    """
    Trigger the Celery task to generate a report.
    """
    try:
        generate_report.delay()
        return Response({"message": "Report generation started"}, status=status.HTTP_202_ACCEPTED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# API View to fetch the latest generated report
@api_view(['GET'])
def latest_report_view(request):
    """
    Fetch the latest report from the reports/ directory.
    """
    try:
        reports_path = Path("reports/")  # Ensure this points to the correct directory
        if not reports_path.exists():
            return Response({"error": "No reports directory found."}, status=status.HTTP_404_NOT_FOUND)

        report_files = list(reports_path.glob("*.json"))
        if not report_files:
            return Response({"error": "No reports available."}, status=status.HTTP_404_NOT_FOUND)

        latest_file = max(report_files, key=lambda x: x.stat().st_mtime)  # Get the most recently modified report
        with open(latest_file, "r") as file:
            report_data = json.load(file)
        return Response(report_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Could not read the report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
