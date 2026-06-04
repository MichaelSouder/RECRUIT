"""Maps legacy database primary keys to RECRUIT row ids (one row per legacy source row)."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from app.database import Base


class LegacyIdMap(Base):
    __tablename__ = "legacy_id_map"
    __table_args__ = (
        UniqueConstraint(
            "source_system",
            "source_table",
            "source_pk",
            name="uq_legacy_id_map_source_row",
        ),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_system = Column(String(64), nullable=False, index=True)
    source_table = Column(String(255), nullable=False)
    source_pk = Column(String(255), nullable=False)
    target_table = Column(String(64), nullable=False, index=True)
    target_pk = Column(Integer, nullable=False, index=True)
    batch_id = Column(String(64), nullable=False, index=True)
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
