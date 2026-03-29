import datetime
from email.policy import default
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255) ,unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

    scripts: Mapped[list["Script"]] = relationship(back_populates="application" , cascade="all, delete-orphan")

class Script(Base):
    __tablename__ = "scripts"

    id:Mapped[int] = mapped_column(primary_key=True, index=True)
    name:Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    default_threads: Mapped[int] = mapped_column(Integer , default=50)
    default_durations: Mapped[int] = mapped_column(Integer, default=300)
    default_rampup: Mapped[int] = mapped_column(Integer, default=30)

    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))

    application: Mapped["Application"] = relationship(back_populates="scripts")

class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    script_id: Mapped[int] = mapped_column(ForeignKey("scripts.id"))
    thread_count: Mapped[int] = mapped_column(Integer)
    duration: Mapped[int] = mapped_column(Integer)
    ramp_up: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    result_file: Mapped[str] = mapped_column(String(512) , nullable=True)
    
    script: Mapped["Script"] = relationship("Script")

def __repr__(self) -> str:
    return f"Application(id={self.id!r}, name={self.name!r})"
