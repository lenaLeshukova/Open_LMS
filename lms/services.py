from decimal import Decimal, InvalidOperation

import stripe
from django.conf import settings

# Инициализируем ключ
stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_product(name, description=""):
    """Создание продукта в Stripe."""
    product = stripe.Product.create(
        name=name,
        description=description
    )
    return product.get('id')

def create_stripe_price(product_id, amount, currency="usd"):
    """Создание цены для существующего продукта с валидацией Decimal."""
    try:
        # Конвертируем в Decimal для защиты от погрешностей float
        decimal_amount = Decimal(str(amount))
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError("Сумма должна быть корректным числом.")

    if decimal_amount <= 0:
        raise ValueError("Сумма оплаты должна быть больше нуля.")

    # Переводим в центы/копейки (минимальные единицы валюты)
    stripe_amount = int(decimal_amount * 100)

    price = stripe.Price.create(
        product=product_id,
        unit_amount=stripe_amount,
        currency=currency,
    )
    return price.get('id')

def create_stripe_checkout_session(price_id):
    """Создание сессии Checkout с использованием актуального синтаксиса."""
    # ИСПРАВЛЕНО: Вместо stripe.Checkout.create используется stripe.checkout.Session.create
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0",  # Куда вернуть при успехе
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
    )
    return session.get('url'), session.get('id')


def retrieve_stripe_checkout_session(session_id):
    """Получение статуса сессии Stripe с использованием актуального синтаксиса."""
    # ИСПРАВЛЕНО: Вместо stripe.Checkout.Session.retrieve используется stripe.checkout.Session.retrieve
    session = stripe.checkout.Session.retrieve(session_id)
    return session.get('payment_status')  # Вернет 'paid', 'unpaid' и т.д.
