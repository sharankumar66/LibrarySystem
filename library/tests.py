from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Author, Book, BorrowRecord
from datetime import datetime

class BorrowRecordTests(APITestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        
        # Create an author
        self.author = Author.objects.create(name="John Doe", bio="Test Author Bio")
        
        # Create a book
        self.book = Book.objects.create(
            title="Sample Book",
            author=self.author,
            isbn="1234567890123",
            available_copies=2
        )
        
        # Endpoint for borrowing and returning
        self.borrow_url = reverse('borrowrecord-borrow-book')
        self.return_url = lambda pk: reverse('borrowrecord-return-book', kwargs={'pk': pk})

    def test_borrow_book_success(self):
        """
        Test borrowing a book when copies are available.
        """
        response = self.client.post(self.borrow_url, {"book_id": self.book.id, "borrowed_by": "Alice"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Book borrowed successfully")
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)  # One copy should be deducted

    def test_borrow_book_no_copies(self):
        """
        Test borrowing a book when no copies are available.
        """
        self.book.available_copies = 0
        self.book.save()

        response = self.client.post(self.borrow_url, {"book_id": self.book.id, "borrowed_by": "Alice"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "No available copies")

    def test_return_book_success(self):
        """
        Test returning a book successfully.
        """
        # Borrow the book first
        borrow_record = BorrowRecord.objects.create(
            book=self.book,
            borrowed_by="Alice",
            borrow_date=datetime.now()
        )
        self.book.available_copies -= 1
        self.book.save()

        response = self.client.put(self.return_url(borrow_record.id))  # Use PUT instead of POST
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Book returned successfully")
        borrow_record.refresh_from_db()
        self.assertIsNotNone(borrow_record.return_date)  # Return date should be set
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)  # Copies should increment

    def test_return_book_already_returned(self):
        """
        Test attempting to return a book that has already been returned.
        """
        # Borrow the book and return it
        borrow_record = BorrowRecord.objects.create(
            book=self.book,
            borrowed_by="Alice",
            borrow_date=datetime.now(),
            return_date=datetime.now()  # Book already returned
        )

        response = self.client.put(self.return_url(borrow_record.id))  # Use PUT instead of POST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Book already returned")
