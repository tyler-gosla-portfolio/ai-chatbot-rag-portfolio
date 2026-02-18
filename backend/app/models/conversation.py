import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Table, Uuid
from sqlalchemy.orm import relationship

from app.database import Base

# Association table for the many-to-many link between conversations and documents.
ConversationDocument = Table(
    "conversation_documents",
    Base.metadata,
    Column(
        "conversation_id",
        Uuid,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "document_id",
        Uuid,
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(500))
    model = Column(String(100), nullable=False, default="gpt-4o")
    system_prompt = Column(Text)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document", secondary=ConversationDocument, backref="conversations"
    )
