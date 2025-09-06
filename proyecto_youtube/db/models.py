from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .session import Base
import datetime


class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True)
    text = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resultados = relationship('Resultado', back_populates='keyword')


class Canal(Base):
    __tablename__ = 'canales'
    id = Column(Integer, primary_key=True)
    channel_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255))
    subscriber_count = Column(Integer)
    view_count = Column(Integer)
    video_count = Column(Integer)
    description = Column(Text)
    resultados = relationship('Resultado', back_populates='canal')


class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    video_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    published_at = Column(DateTime)


class Resultado(Base):
    __tablename__ = 'resultados'
    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'))
    canal_id = Column(Integer, ForeignKey('canales.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    competencia_tipo = Column(String(32))
    recurrente = Column(String(8))
    origin_keywords = Column(Text)
    recent_avg_views = Column(Integer)
    recent_median_views = Column(Integer)
    # Store full raw niche result as JSON text for flexibility
    raw_result = Column(Text)

    keyword = relationship('Keyword', back_populates='resultados')
    canal = relationship('Canal', back_populates='resultados')
