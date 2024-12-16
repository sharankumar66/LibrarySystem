import os
from datetime import datetime
from celery import shared_task
from .models import Author, Book, BorrowRecord
import json

@shared_task
def generate_report():
    # Ensure the reports directory exists
    reports_dir = 'reports/'
    os.makedirs(reports_dir, exist_ok=True)

    # Collect data for the report
    total_authors = Author.objects.count()
    total_books = Book.objects.count()
    total_borrowed_books = BorrowRecord.objects.filter(returned=False).count()  # Only unreturned books are considered

    # Generate the report dictionary
    report_data = {
        "total_authors": total_authors,
        "total_books": total_books,
        "total_borrowed_books": total_borrowed_books,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Create a timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"report_{timestamp}.json"
    report_path = os.path.join(reports_dir, report_filename)

    # Save the report to a JSON file
    with open(report_path, 'w') as report_file:
        json.dump(report_data, report_file, indent=4)

    return report_filename
