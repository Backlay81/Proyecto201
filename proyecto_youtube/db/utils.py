from .session import SessionLocal, engine, Base
from .models import Keyword, Canal, Resultado
from sqlalchemy.orm import Session


def init_db():
    Base.metadata.create_all(bind=engine)


def save_result(session: Session, keyword_text: str, canal_data: dict):
    # Ensure keyword
    kw = session.query(Keyword).filter_by(text=keyword_text).first()
    if not kw:
        kw = Keyword(text=keyword_text)
        session.add(kw)
        session.commit()

    # Ensure canal
    ch = session.query(Canal).filter_by(channel_id=canal_data.get('channelId')).first()
    if not ch:
        ch = Canal(
            channel_id=canal_data.get('channelId'),
            title=canal_data.get('title'),
            subscriber_count=canal_data.get('subscriberCount'),
            view_count=canal_data.get('viewCount'),
            video_count=canal_data.get('videoCount'),
            description=canal_data.get('description')
        )
        session.add(ch)
        session.commit()

    # Add resultado
    res = Resultado(
        keyword_id=kw.id,
        canal_id=ch.id,
        competencia_tipo=canal_data.get('competencia_tipo'),
        recurrente=str(canal_data.get('recurrente')),
        origin_keywords=canal_data.get('origin_keywords'),
        recent_avg_views=canal_data.get('avg_views'),
        recent_median_views=canal_data.get('median_views')
    )
    session.add(res)
    session.commit()
    return res


def save_niche_result(session: Session, niche_data: dict):
    # Ensure keyword
    kw = session.query(Keyword).filter_by(text=niche_data.get('keyword')).first()
    if not kw:
        kw = Keyword(text=niche_data.get('keyword'))
        session.add(kw)
        session.commit()

    import json
    res = Resultado(
        keyword_id=kw.id,
        canal_id=None,
        competencia_tipo=niche_data.get('automatizable'),
        recurrente='False',
        origin_keywords=None,
        recent_avg_views=int(niche_data.get('avg_views') or 0),
        recent_median_views=0,
        raw_result=json.dumps(niche_data, ensure_ascii=False)
    )
    session.add(res)
    session.commit()
    return res
