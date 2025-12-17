"""WhatsApp verification service using Twilio"""
import os
import random
from datetime import datetime, timedelta
from twilio.rest import Client
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from models.user import User, PhoneVerification, UserStatus

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")


class WhatsAppService:
    def __init__(self):
        self.client = None
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code"""
        return str(random.randint(100000, 999999))

    async def send_verification_code(
        self,
        phone_number: str,
        user_id: int,
        db: Session
    ) -> PhoneVerification:
        """Send verification code via WhatsApp"""
        # Generate code
        code = self.generate_verification_code()

        # Create verification record
        verification = PhoneVerification(
            user_id=user_id,
            phone_number=phone_number,
            verification_code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )

        db.add(verification)
        db.commit()
        db.refresh(verification)

        # Send via Twilio WhatsApp
        if self.client:
            try:
                message = self.client.messages.create(
                    body=f"🔐 Seu código de verificação ApoloCopilot é: {code}\n\nVálido por 15 minutos.",
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{phone_number}"
                )
                print(f"✅ WhatsApp sent: {message.sid}")
            except Exception as e:
                print(f"❌ WhatsApp error: {e}")
                # In development, allow to continue without actually sending
                pass
        else:
            print(f"⚠️ Twilio not configured. Code: {code}")

        return verification

    async def verify_code(
        self,
        phone_number: str,
        code: str,
        db: Session
    ) -> bool:
        """Verify the code sent to phone number"""
        verification = db.query(PhoneVerification).filter(
            PhoneVerification.phone_number == phone_number,
            PhoneVerification.is_verified == False,
            PhoneVerification.expires_at > datetime.utcnow()
        ).order_by(PhoneVerification.created_at.desc()).first()

        if not verification:
            return False

        # Increment attempts
        verification.attempts += 1

        if verification.verification_code == code:
            # Code is correct
            verification.is_verified = True
            verification.verified_at = datetime.utcnow()

            # Update user status
            user = db.query(User).filter(User.id == verification.user_id).first()
            if user:
                user.phone_number = phone_number
                user.status = UserStatus.PENDING_DOCUMENTS

            db.commit()
            return True
        else:
            # Code is incorrect
            db.commit()

            # Block after 5 attempts
            if verification.attempts >= 5:
                verification.expires_at = datetime.utcnow()
                db.commit()

            return False

    async def resend_code(
        self,
        phone_number: str,
        user_id: int,
        db: Session
    ) -> PhoneVerification:
        """Resend verification code"""
        # Expire old verifications
        db.query(PhoneVerification).filter(
            PhoneVerification.phone_number == phone_number,
            PhoneVerification.is_verified == False
        ).update({"expires_at": datetime.utcnow()})
        db.commit()

        # Send new code
        return await self.send_verification_code(phone_number, user_id, db)
