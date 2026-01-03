"""Document verification routes"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import get_db
from models.user import User, DocumentType, DocumentVerification
from utils.security import get_current_active_user
from services.document_service import DocumentService

router = APIRouter(prefix="/api/documents", tags=["Documents"])
document_service = DocumentService()


class DocumentResponse(BaseModel):
    id: int
    document_type: str
    status: str
    uploaded_at: str
    rejection_reason: str | None

    class Config:
        from_attributes = True


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload a document for verification"""
    try:
        # Validate document type
        try:
            doc_type = DocumentType(document_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de documento inválido. Use: {', '.join([t.value for t in DocumentType])}",
            )

        # Upload document
        document = await document_service.upload_document(
            user_id=current_user.id, document_type=doc_type, file=file, db=db
        )

        return {
            "success": True,
            "message": "Documento enviado com sucesso. Aguarde análise.",
            "document_id": document.id,
            "status": document.status.value,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload: {str(e)}",
        )


@router.get("/my-documents", response_model=List[DocumentResponse])
async def get_my_documents(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get current user's documents"""
    documents = await document_service.get_user_documents(user_id=current_user.id, db=db)

    return documents


@router.get("/required")
async def get_required_documents():
    """Get list of required documents"""
    return {
        "required": [
            {
                "type": "id_card",
                "name": "Documento de Identidade (RG/CNH)",
                "description": "Foto clara do seu documento de identidade",
            },
            {
                "type": "proof_of_address",
                "name": "Comprovante de Residência",
                "description": "Conta de luz, água ou telefone (últimos 3 meses)",
            },
        ],
        "optional": [
            {"type": "passport", "name": "Passaporte", "description": "Se tiver passaporte válido"}
        ],
        "accepted_formats": ["PDF", "JPG", "JPEG", "PNG"],
        "max_size_mb": 10,
    }
