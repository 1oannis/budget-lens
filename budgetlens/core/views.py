"""Views for the core app"""

import base64
import logging
import json
import os
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from openai import OpenAI
from .forms import ExpenseForm
from .models import Expense, UserProfile


OPEN_EXCHANGE_RATES_API_KEY = os.getenv("OPEN_EXCHANGE_RATES_API_KEY")
OPEN_EXCHANGE_RATES_API_URL = "https://openexchangerates.org/api/historical/"

log = logging.getLogger(__name__)
client = OpenAI()


def encode_image(image_path):
    """Encode the image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_receipt(image_path):
    """Process the receipt image using OpenAI API"""
    log.debug("views : process_receipt()")
    base64_image = encode_image(image_path)
    category = "Sample Category"
    expense_date = "2024-11-13"
    amount = 10.00
    currency = "EUR"

    base_categories = (
        "Housing,Utilities,Transportation,Groceries,Dining Out,Healthcare,"
        "Debt Payments,Insurance,Clothing,Entertainment,"
        "Education,Childcare,Pet Care,Subscriptions,Miscellaneous"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze the provided receipt and extract the following details: "
                            "1. Category: Determine the category of the expense from this list: "
                            f"{base_categories}. 2. Date: Identify the transaction date. "
                            "3. Amount: Extract the expense amount as a decimal number. Consider: "
                            "- A comma may serve as a thousand separator or decimal separator. "
                            "- In KRW (Korean Won), the amount is never lower than a thousand. "
                            "4. Currency: Identify the currency used in the expense "
                            "(three-character ISO 4217 code). Respond strictly in JSON format, "
                            "starting and ending with braces, without any additional markup or "
                            "explanation. Example response: {\"category\": \"<category>\","
                            " \"date\": \"<date>\", \"amount\": <amount>,"
                            " \"currency\": \"<currency>\"}"
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    log.debug("Response from OpenAI")
    log.debug(response.choices[0].message.content)

    if response.choices[0].message.content is None:
        log.error("Error in response")
        return category, expense_date, amount, currency

    response_data = json.loads(response.choices[0].message.content)

    category = response_data.get("category")
    expense_date = response_data.get("date")
    amount = response_data.get("amount")
    currency = response_data.get("currency")

    return category, expense_date, amount, currency


def get_exchange_rate(date, from_currency, to_currency):
    """Get the exchange rate for the given date and currencies"""

    if from_currency == to_currency:
        return 1, 1

    log.debug("views : get_exchange_rate()")
    url = f"{OPEN_EXCHANGE_RATES_API_URL}{date}.json"
    log.debug("URL: %s", url)
    params = {"app_id": OPEN_EXCHANGE_RATES_API_KEY}
    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 200:
        data = response.json()
        return data["rates"].get(from_currency), data["rates"].get(to_currency)

    log.error("Error fetching exchange rate: %s", response.text)
    return None, None


@login_required
def upload_receipt(request):
    """View to upload the receipt image and process it"""
    response = None
    log.debug("views : upload_receipt()")
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            category, expense_date, amount, currency = process_receipt(
                expense.receipt_image.path
            )

            expense.category = category
            expense.expense_date = expense_date
            expense.amount = amount
            expense.currency = currency

            user_profile = UserProfile.objects.get(user_id=request.user.id)
            target_currency = user_profile.target_currency

            exchange_rate_to_usd, exchange_rate_to_target = get_exchange_rate(
                expense_date, currency, target_currency
            )
            log.debug(
                "Exchange rates: to USD %s, to target %s",
                exchange_rate_to_usd,
                exchange_rate_to_target,
            )
            if exchange_rate_to_usd and exchange_rate_to_target:
                converted_amount_to_usd = amount / exchange_rate_to_usd
                converted_amount_to_target = (
                    converted_amount_to_usd * exchange_rate_to_target
                )
                log.debug("Converted amount: %s", converted_amount_to_target)
                expense.amount_in_target_currency = round(converted_amount_to_target, 2)
            else:
                log.error("Could not convert amount to target currency")

            expense.save()

            response = {
                "category": category,
                "expense_date": expense_date,
                "amount": amount,
                "currency": currency,
                "amount_in_target_currency": expense.amount_in_target_currency,
            }
        else:
            log.error("Form errors: %s", form.errors)
    else:
        form = ExpenseForm()
    return render(request, "upload.html", {"form": form, "response": response})


@login_required
def dashboard(request):
    """View to display the user's expenses"""
    expenses = Expense.objects.filter(user=request.user)
    return render(request, "dashboard.html", {"expenses": expenses})
