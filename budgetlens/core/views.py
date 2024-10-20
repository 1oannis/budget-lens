import pytesseract
from PIL import Image
import re
from django.shortcuts import render, redirect, get_object_or_404
from .models import Receipt
from .forms import ReceiptUploadForm
from django.core.files.storage import default_storage
from pdf2image import convert_from_path

def upload_receipt(request):
    if request.method == 'POST':
        form = ReceiptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.user = request.user
            receipt.save()

            # Process the receipt with OCR and extract necessary data
            process_receipt_ocr(receipt)

            return redirect('receipt_detail', receipt_id=receipt.receipt_id)
    else:
        form = ReceiptUploadForm()
    return render(request, 'core/upload_receipt.html', {'form': form})

def process_receipt_ocr(receipt):
    """
    Processes the uploaded receipt image/PDF using Tesseract OCR and parses the result to extract:
    - Merchant name
    - Date
    - Amount
    - Description
    """
    # Open the image or PDF
    if receipt.image_path.path.endswith('.pdf'):
        # Handle PDFs - For simplicity, we'll assume 1-page PDFs and convert to image
        images = convert_from_path(receipt.image_path.path)
        image = images[0]  # Taking only the first page
    else:
        image = Image.open(receipt.image_path.path)

    # Perform OCR with Tesseract
    ocr_result = pytesseract.image_to_string(image, lang='eng+deu+kor+ell')

    # Parse the OCR result using regular expressions and custom logic
    merchant_name = extract_merchant_name(ocr_result)
    date = extract_date(ocr_result)
    amount = extract_amount(ocr_result)
    description = extract_description(ocr_result)

    # Save the parsed data into the receipt model
    receipt.merchant_name = merchant_name
    receipt.date = date
    receipt.amount = amount
    receipt.description = description
    receipt.save()

def extract_merchant_name(text):
    """
    A very basic approach to extracting merchant name. This would likely require NLP in a real-world scenario.
    """
    # Assume first line is merchant name, further parsing can be added later
    return text.split('\n')[0]

def extract_date(text):
    """
    Extract a date in formats like MM/DD/YYYY, DD/MM/YYYY, or YYYY-MM-DD using regex.
    """
    date_pattern = r'\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b'
    match = re.search(date_pattern, text)
    if match:
        return match.group(0)
    return None

def extract_amount(text):
    """
    Extract an amount from the text using regex. We'll search for patterns like '€123.45' or '123,45 USD'.
    """
    amount_pattern = r'(\d+[.,]\d{2})\s*(USD|EUR|₩|KRW|GBP|£)?'
    match = re.search(amount_pattern, text)
    if match:
        amount_str = match.group(1).replace(',', '.')
        return float(amount_str)  # Convert to float for saving as DecimalField
    return None

def extract_description(text):
    """
    Extracts the description, for simplicity taking the second line.
    """
    lines = text.split('\n')
    return lines[1] if len(lines) > 1 else "No Description"

def receipt_detail(request, receipt_id):
    receipt = get_object_or_404(Receipt, receipt_id=receipt_id)
    return render(request, 'core/receipt_detail.html', {'receipt': receipt})

def index(request):
    return render(request, 'core/index.html')
