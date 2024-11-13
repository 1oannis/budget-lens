import base64
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from openai import OpenAI
from .forms import ExpenseForm
from .models import Expense
import json

client = OpenAI()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_receipt(image_path):
    print("views : process_receipt()")
    base64_image = encode_image(image_path)
    category = "Sample Category"
    expense_date = "2024-11-13"
    amount = 10.00
    currency = "EUR"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this receipt. Tell me the category, date, amount(decimal) and currency (three characters) of the expense. Respond in the json format: {category: <category>, date: <date>, amount: <amount>, currency: <currency>} . Don't use any extra markup language just the JSON beginning and ending with the braces.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":  f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
    )

    print("Response from OpenAI")
    print(response.choices[0].message.content)

    if response.choices[0].message.content is None:
        print("Error in response")
        return category, expense_date, amount, currency

    response_data = json.loads(response.choices[0].message.content)

    category = response_data.get("category")
    expense_date = response_data.get("date")
    amount = response_data.get("amount")
    currency = response_data.get("currency")

    return category, expense_date, amount, currency


@login_required
def upload_receipt(request):
    response = None
    print("views : upload_receipt()")
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            # Process the receipt image
            category, expense_date, amount, currency = process_receipt(expense.receipt_image.path)
            # Update the expense instance
            expense.category = category
            expense.expense_date = expense_date
            expense.amount = amount
            expense.save()
            # Prepare the response to display
            response = {
                'category': category,
                'expense_date': expense_date,
                'amount': amount,
                'currency': currency,
            }
        else:
            print("Form errors:", form.errors)
    else:
        form = ExpenseForm()
    return render(request, 'upload.html', {'form': form, 'response': response})

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'expenses': expenses})
