"""WhatsApp verification routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.user import User
from utils.security import get_current_active_user
from services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])
whatsapp_service = WhatsAppService()


class PhoneNumber(BaseModel):
    phone_number: str


class VerificationCode(BaseModel):
    phone_number: str
    code: str


@router.post("/send-code")
async def send_verification_code(
    data: PhoneNumber,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send verification code via WhatsApp"""
    try:
        verification = await whatsapp_service.send_verification_code(
            phone_number=data.phone_number,
            user_id=current_user.id,
            db=db
        )

        return {
            "success": True,
            "message": "Código de verificação enviado via WhatsApp",
            "phone_number": data.phone_number,
            "expires_in_minutes": 15
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar código: {str(e)}"
        )


@router.post("/verify-code")
async def verify_code(
    data: VerificationCode,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify WhatsApp code"""
    is_valid = await whatsapp_service.verify_code(
        phone_number=data.phone_number,
        code=data.code,
        db=db
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido ou expirado"
        )

    return {
        "success": True,
        "message": "Número verificado com sucesso!",
        "next_step": "upload_documents"
    }


@router.post("/resend-code")
async def resend_verification_code(
    data: PhoneNumber,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Resend verification code"""
    try:
        verification = await whatsapp_service.resend_code(
            phone_number=data.phone_number,
            user_id=current_user.id,
            db=db
        )

        return {
            "success": True,
            "message": "Novo código enviado via WhatsApp"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao reenviar código: {str(e)}"
        )
