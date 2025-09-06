from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .session import Base
import datetime


# ===== MÓDULO NICHOS =====
class NicheKeyword(Base):
    __tablename__ = 'niche_keywords'
    id = Column(Integer, primary_key=True)
    text = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resultados = relationship('NicheResult', back_populates='keyword')


class NicheResult(Base):
    __tablename__ = 'niche_results'
    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('niche_keywords.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Niche analysis data
    video_count = Column(Integer)
    avg_views = Column(Integer)
    median_views = Column(Integer)
    pct75_views = Column(Integer)
    max_views = Column(Integer)
    decision = Column(String(32))
    reason = Column(Text)
    base_score = Column(Integer)
    opportunity_score = Column(Integer)
    # Store full raw result as JSON for flexibility
    raw_result = Column(Text)

    keyword = relationship('NicheKeyword', back_populates='resultados')


# ===== MÓDULO CANALES =====
class ChannelKeyword(Base):
    __tablename__ = 'channel_keywords'
    id = Column(Integer, primary_key=True)
    text = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resultados = relationship('ChannelResult', back_populates='keyword')


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    channel_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255))
    subscriber_count = Column(Integer)
    view_count = Column(Integer)
    video_count = Column(Integer)
    description = Column(Text)
    resultados = relationship('ChannelResult', back_populates='canal')


class ChannelResult(Base):
    __tablename__ = 'channel_results'
    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('channel_keywords.id'))
    canal_id = Column(Integer, ForeignKey('channels.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    competencia_tipo = Column(String(32))
    recurrente = Column(String(8))
    origin_keywords = Column(Text)
    recent_avg_views = Column(Integer)
    recent_median_views = Column(Integer)
    # Store full raw result as JSON
    raw_result = Column(Text)

    keyword = relationship('ChannelKeyword', back_populates='resultados')
    canal = relationship('Channel', back_populates='resultados')


# ===== TABLAS COMPARTIDAS =====
class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    video_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    published_at = Column(DateTime)


# ===== LEGACY TABLES (para migración) =====
# Estas se mantienen para compatibilidad pero se deprecan
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
    raw_result = Column(Text)

    keyword = relationship('Keyword', back_populates='resultados')
    canal = relationship('Canal', back_populates='resultados')
