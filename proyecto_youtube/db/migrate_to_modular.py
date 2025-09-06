#!/usr/bin/env python3
"""
Migración a esquema modular de base de datos
Crea las nuevas tablas separadas por módulo
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from db.session import SessionLocal, engine, Base
from db.models import (
    NicheKeyword, NicheResult,
    ChannelKeyword, Channel, ChannelResult
)


def migrate_to_modular_schema():
    """Crear nuevas tablas modulares"""

    print("🔄 Creando esquema modular de base de datos...")

    try:
        # Crear todas las tablas (incluyendo las nuevas)
        Base.metadata.create_all(bind=engine)

        print("✅ Esquema modular creado exitosamente:")
        print("   📊 niche_keywords, niche_results")
        print("   📺 channel_keywords, channels, channel_results")
        print("   🔄 videos (compartida)")
        print("   🏛️  Tablas legacy preservadas para compatibilidad")

        # Verificar que las tablas se crearon
        with SessionLocal() as session:
            # Test query en cada tabla nueva
            niche_count = session.query(NicheKeyword).count()
            channel_count = session.query(ChannelKeyword).count()
            channels_count = session.query(Channel).count()

            print("\n📈 Verificación de tablas:")
            print(f"   Niche keywords: {niche_count} registros")
            print(f"   Channel keywords: {channel_count} registros")
            print(f"   Channels: {channels_count} registros")

    except Exception as e:
        print(f"❌ Error durante creación de esquema: {e}")
        raise


if __name__ == "__main__":
    migrate_to_modular_schema()
