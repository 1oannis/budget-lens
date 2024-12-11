"""Views for the core app"""

import base64
from decimal import Decimal
import logging
import json
import os
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from openai import OpenAI
from .forms import ExpenseEditForm, ExpenseForm
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
                            "4. Currency: Identify the currency used in the expense starting "
                            "(three-character ISO 4217 code). Respond strictly in JSON format, "
                            "and ending with braces, without any additional markup language "
                            'or explanation. Example response: {"category": "<category>",'
                            ' "date": "<date>", "amount": <amount>,'
                            ' "currency": "<currency>"}'
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

    try:
        if (
            not response
            or not response.choices
            or not response.choices[0].message.content
        ):
            raise ValueError("Empty or invalid response from OpenAI API")

        content = response.choices[0].message.content.strip()
        log.debug("Response from OpenAI")
        log.debug(content)

        if content.startswith("```json") and content.endswith("```"):
            log.debug("Content: %s", content)
            content = content[7:-3].strip()
            log.debug("Content after stripping markdown: %s", content)

        response_data = json.loads(content)

        if "/" in response_data.get("date"):
            response_data["date"] = response_data["date"].replace("/", "-")

        category = response_data.get("category")
        expense_date = response_data.get("date")
        amount = response_data.get("amount")
        currency = response_data.get("currency").upper()

        return category, expense_date, amount, currency
    except json.JSONDecodeError as e:
        log.error("JSON decode error: %s", e)
        raise
    except ValueError as e:
        log.error("Value error: %s", e)
        raise
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise


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
    log.debug("views : upload_receipt()")
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense_dto = form.save(commit=False)
            expense_dto.user = request.user
            expense_dto.save()

            category, expense_date, amount, currency = process_receipt(
                expense_dto.receipt_image.path
            )

            expense_dto.category = category
            expense_dto.expense_date = expense_date
            expense_dto.amount = amount
            expense_dto.currency = currency

            user_profile = UserProfile.objects.get(user=request.user)
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
                exchange_rate_to_usd = Decimal(str(exchange_rate_to_usd))
                exchange_rate_to_target = Decimal(str(exchange_rate_to_target))
                amount_decimal = Decimal(str(amount))

                converted_amount_to_usd = amount_decimal / exchange_rate_to_usd
                converted_amount_to_target = converted_amount_to_usd * exchange_rate_to_target
                expense_dto.amount_in_target_currency = round(converted_amount_to_target, 2)
                log.debug("Converted amount: %s", expense_dto.amount_in_target_currency)
            else:
                log.error("Could not convert amount to target currency")

            expense_dto.save()
            # Redirect to the expense page to adjust information
            return redirect('expense', expense_id=expense_dto.id)
        else:
            log.error("Form errors: %s", form.errors)
    else:
        form = ExpenseForm()
    return render(request, "upload.html", {"form": form})


@login_required
def dashboard(request):
    """View to display the user's expenses"""
    expenses = Expense.objects.filter(user=request.user)
    return render(request, "dashboard.html", {"expenses": expenses})


@login_required
def expense(request, expense_id):
    """View to display the details of a specific expense"""
    log.debug("views : expense()")
    log.debug("Expense ID: %s", expense_id)
    expense_detail = Expense.objects.get(id=expense_id, user=request.user)
    log.debug("Expense detail: %s", expense_detail.expense_date)
    log.debug("User Currency: %s", request.user.userprofile.target_currency)
    return render(
        request, "expense.html", {"expense": expense_detail, "user": request.user}
    )


@login_required
def save_expense(request, expense_id):
    """View to save the edited expense details with currency conversion"""
    log.debug("views : save_expense()")
    expense_edit = Expense.objects.get(id=expense_id, user=request.user)

    if request.method == "POST":
        form = ExpenseEditForm(request.POST, instance=expense_edit)
        if form.is_valid():
            expense_form = form.save(commit=False)

            user_profile = UserProfile.objects.get(user=request.user)
            target_currency = user_profile.target_currency

            exchange_rate_to_usd, exchange_rate_to_target = get_exchange_rate(
                expense_form.expense_date, expense_form.currency, target_currency
            )

            if exchange_rate_to_usd and exchange_rate_to_target:
                exchange_rate_to_usd = Decimal(str(exchange_rate_to_usd))
                exchange_rate_to_target = Decimal(str(exchange_rate_to_target))

                converted_amount_to_usd = expense_form.amount / exchange_rate_to_usd
                converted_amount_to_target = (
                    converted_amount_to_usd * exchange_rate_to_target
                )
                expense_form.amount_in_target_currency = round(
                    converted_amount_to_target, 2
                )

            expense_form.save()
            log.debug("Expense updated successfully")
            return redirect("expense", expense_id=expense_id)
        else:
            log.error("Form errors: %s", form.errors)
    else:
        form = ExpenseEditForm(instance=expense_edit)

    return render(
        request,
        "expense.html",
        {"form": form, "expense": expense_edit, "user": request.user},
    )
