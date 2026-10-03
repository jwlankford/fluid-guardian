import os
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
import stripe

from fg_core.db.session import get_session
from fg_core.models.user_account import UserAccount

# Make sure to set these environment variables when running!
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")
PRICE_ID = os.getenv("STRIPE_PRICE_ID", "price_placeholder")

router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/create-checkout-session")
def create_checkout_session(user_id: str):
    """
    Creates a Stripe Checkout session for the user to buy 50 scans.
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": PRICE_ID,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url="http://localhost:5173/dashboard?success=true",
            cancel_url="http://localhost:5173/dashboard?canceled=true",
            client_reference_id=user_id, # Very important: tells us which user bought it
        )
        return {"url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_session)):
    """
    Stripe hits this endpoint after a successful payment.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        
        if user_id:
            # Grant the user 50 credits
            user = db.scalar(select(UserAccount).where(UserAccount.user_id == user_id))
            if not user:
                user = UserAccount(user_id=user_id, credits=50)
                db.add(user)
            else:
                user.credits += 50
            db.commit()

    return {"status": "success"}
