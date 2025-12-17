"""Document verification service"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import BinaryIO
from fastapi import UploadFile
from sqlalchemy.orm import Session
from PIL import Image

from models.user import DocumentVerification, DocumentType, DocumentStatus, User, UserStatus


class DocumentService:
    def __init__(self):
        self.upload_dir = Path("uploads/documents")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.allowed_extensions = {
            "pdf", "jpg", "jpeg", "png", "doc", "docx"
        }
        self.max_size = 10 * 1024 * 1024  # 10MB

    def _validate_file(self, file: UploadFile) -> tuple[bool, str]:
        """Validate uploaded file"""
        # Check extension
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in self.allowed_extensions:
            return False, f"Tipo de arquivo não permitido. Use: {', '.join(self.allowed_extensions)}"

        return True, ""

    def _save_file(self, file: UploadFile, user_id: int, doc_type: str) -> str:
        """Save uploaded file to disk"""
        file_ext = file.filename.split(".")[-1].lower()
        unique_filename = f"{user_id}_{doc_type}_{uuid.uuid4()}.{file_ext}"
        file_path = self.upload_dir / unique_filename

        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        # Optimize image if it's an image
        if file_ext in {"jpg", "jpeg", "png"}:
            try:
                img = Image.open(file_path)
                # Resize if too large
                max_dimension = 2000
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.LANCZOS)
                    img.save(file_path, optimize=True, quality=85)
            except Exception as e:
                print(f"Image optimization error: {e}")

        return str(file_path)

    async def upload_document(
        self,
        user_id: int,
        document_type: DocumentType,
        file: UploadFile,
        db: Session
    ) -> DocumentVerification:
        """Upload and save document for verification"""
        # Validate file
        is_valid, error_msg = self._validate_file(file)
        if not is_valid:
            raise ValueError(error_msg)

        # Save file
        file_path = self._save_file(file, user_id, document_type.value)

        # Create verification record
        document = DocumentVerification(
            user_id=user_id,
            document_type=document_type,
            file_path=file_path,
            status=DocumentStatus.PENDING
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    async def approve_document(
        self,
        document_id: int,
        db: Session
    ) -> DocumentVerification:
        """Approve a document"""
        document = db.query(DocumentVerification).filter(
            DocumentVerification.id == document_id
        ).first()

        if not document:
            raise ValueError("Document not found")

        document.status = DocumentStatus.APPROVED
        document.reviewed_at = datetime.utcnow()

        # Check if user has all required documents approved
        user = db.query(User).filter(User.id == document.user_id).first()
        if user:
            required_docs = {DocumentType.ID_CARD, DocumentType.PROOF_OF_ADDRESS}
            approved_docs = db.query(DocumentVerification).filter(
                DocumentVerification.user_id == user.id,
                DocumentVerification.status == DocumentStatus.APPROVED
            ).all()

            approved_types = {doc.document_type for doc in approved_docs}

            # If all required documents are approved, verify user
            if required_docs.issubset(approved_types):
                user.status = UserStatus.ACTIVE
                user.is_verified = True

        db.commit()
        db.refresh(document)

        return document

    async def reject_document(
        self,
        document_id: int,
        reason: str,
        db: Session
    ) -> DocumentVerification:
        """Reject a document"""
        document = db.query(DocumentVerification).filter(
            DocumentVerification.id == document_id
        ).first()

        if not document:
            raise ValueError("Document not found")

        document.status = DocumentStatus.REJECTED
        document.rejection_reason = reason
        document.reviewed_at = datetime.utcnow()

        db.commit()
        db.refresh(document)

        return document

    async def get_user_documents(
        self,
        user_id: int,
        db: Session
    ) -> list[DocumentVerification]:
        """Get all documents for a user"""
        return db.query(DocumentVerification).filter(
            DocumentVerification.user_id == user_id
        ).order_by(DocumentVerification.uploaded_at.desc()).all()
