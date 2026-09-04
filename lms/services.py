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
    """Создание цены для существующего продукта."""
    # Важно: Stripe принимает сумму в минимальных единицах валюты (центы/копейки).
    # умножаем на 100 и приводим к Integer
    stripe_amount = int(float(amount) * 100)

    price = stripe.Price.create(
        product=product_id,
        unit_amount=stripe_amount,
        currency=currency,
    )
    return price.get('id')

def create_stripe_checkout_session(price_id):
    """Создание сессии Checkout для получения веб-ссылки на оплату."""
    session = stripe.Checkout.create(
        success_url="http://127.0.0",  # Куда вернуть при успехе
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
    )
    return session.get('url'), session.get('id')

def retrieve_stripe_checkout_session(session_id):
    """Получение информации о сессии Stripe для проверки статуса."""
    session = stripe.Checkout.Session.retrieve(session_id)
    return session.get('payment_status') # Вернет 'paid', 'unpaid' или 'no_payment_required'
