from .session import SessionLocal, engine, Base
from .models import (
    # Nuevos modelos separados por módulo
    NicheKeyword, NicheResult,
    ChannelKeyword, Channel, ChannelResult,
    # Legacy models para compatibilidad
    Keyword, Canal, Resultado
)
from sqlalchemy.orm import Session


def init_db():
    Base.metadata.create_all(bind=engine)


# ===== FUNCIONES PARA NICHOS =====
def save_niche_result(session: Session, niche_data: dict):
    """Guardar resultado de análisis de nicho en tabla dedicada"""
    # Ensure keyword
    kw = session.query(NicheKeyword).filter_by(text=niche_data.get('keyword')).first()
    if not kw:
        kw = NicheKeyword(text=niche_data.get('keyword'))
        session.add(kw)
        session.commit()

    import json
    res = NicheResult(
        keyword_id=kw.id,
        video_count=niche_data.get('video_count'),
        avg_views=int(niche_data.get('avg_views') or 0),
        median_views=int(niche_data.get('median_views') or 0),
        pct75_views=int(niche_data.get('pct75_views') or 0),
        max_views=int(niche_data.get('max_views') or 0),
        decision=niche_data.get('decision'),
        reason=niche_data.get('reason'),
        base_score=niche_data.get('base_score'),
        opportunity_score=int(niche_data.get('opportunity_score') or 0),
        raw_result=json.dumps(niche_data, ensure_ascii=False)
    )
    session.add(res)
    session.commit()
    return res


# ===== FUNCIONES PARA CANALES =====
def save_channel_result(session: Session, keyword_text: str, canal_data: dict):
    """Guardar resultado de búsqueda de canales en tabla dedicada"""
    # Ensure keyword
    kw = session.query(ChannelKeyword).filter_by(text=keyword_text).first()
    if not kw:
        kw = ChannelKeyword(text=keyword_text)
        session.add(kw)
        session.commit()

    # Ensure canal
    ch = session.query(Channel).filter_by(channel_id=canal_data.get('channelId')).first()
    if not ch:
        ch = Channel(
            channel_id=canal_data.get('channelId'),
            title=canal_data.get('title'),
            subscriber_count=canal_data.get('subscriberCount'),
            view_count=canal_data.get('viewCount'),
            video_count=canal_data.get('videoCount'),
            description=canal_data.get('description')
        )
        session.add(ch)
        session.commit()

    import json
    # Add resultado
    res = ChannelResult(
        keyword_id=kw.id,
        canal_id=ch.id,
        competencia_tipo=canal_data.get('competencia_tipo'),
        recurrente=str(canal_data.get('recurrente')),
        origin_keywords=canal_data.get('origin_keywords'),
        recent_avg_views=canal_data.get('avg_views'),
        recent_median_views=canal_data.get('median_views'),
        raw_result=json.dumps(canal_data, ensure_ascii=False)
    )
    session.add(res)
    session.commit()
    return res


# ===== FUNCIONES LEGACY (para compatibilidad) =====
def save_result(session: Session, keyword_text: str, canal_data: dict):
    """Función legacy - usa save_channel_result en su lugar"""
    return save_channel_result(session, keyword_text, canal_data)
