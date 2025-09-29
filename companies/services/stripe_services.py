from django.conf import settings
import stripe
from typing import Dict, Any

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_stripe():
    """Returns the intialized Stripe Client + Api Key already activated"""
    return stripe 

def create_payment_intent(amount_in_dollars: float, currency: str ='usd') -> Dict[str, Any]:
    """
        We'll be using this function in our UpgradeToPremium API View to handle the payment system 
            - Once the user paid and the payment was successful, we will go ahead and upgrade their status 
            - We return client secret which is then verified on the frontend 
    """
    intent = get_stripe().PaymentIntent.create(
        amount=int(amount_in_dollars * 100),
        currency=currency,
        # This allows users to pay with all types of payments like Apple Pay, ACH etc...
        automatic_payment_methods= {'enabled': True}
    )
    return intent['client_secret']

def verify_payment(intent_id: str, amount_in_dollars: float, currency: str ='usd'):
    try:
        intent = get_stripe().PaymentIntent.retrieve(intent_id)
        # Checking if our payment is successful on stripe 
        if (intent.success == 'succeeded' 
            and intent.amount_received == int(amount_in_dollars * 100) 
            and intent.currency == currency):
            return True
    except Exception as e:
        return False 