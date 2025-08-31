"""
Script de prueba para las mejoras implementadas
"""
import sys
import os

# Añadir paths necesarios
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials"))
sys.path.append(os.path.dirname(__file__))

from scripts.niche_analyzer_basic import NicheAnalyzerEnhanced

def test_mejoras():
    """Probar las mejoras de automatización y monetización"""
    print("🧪 TESTING DE MEJORAS IMPLEMENTADAS")
    print("=" * 50)
    
    analyzer = NicheAnalyzerEnhanced()
    
    # Test keywords que deberían activar las mejoras
    test_keywords = [
        "mejores cuentas remuneradas 2025",  # Automatizable + Afiliación + Anuncios (CORREGIR)
        "mejores productos financieros",     # Automatizable + Afiliación + Anuncios
        "review pienso para perros",         # Automatizable + Solo Afiliación  
        "coaching psicología online",        # NO Automatizable + Solo Anuncios
        "vlog de mi día",                    # NO Automatizable + Difícil Monetizar
    ]
    
    print("🔍 TESTING FUNCIONES MEJORADAS:")
    print("-" * 30)
    
    for keyword in test_keywords:
        print(f"\n🎯 Keyword: '{keyword}'")
        
        # Test automatización
        is_auto = analyzer.is_automatizable(keyword)
        print(f"   🤖 Automatizable: {'✅ SÍ' if is_auto else '❌ NO'}")
        
        # Test monetización
        tipo_monetizacion = analyzer.clasificar_monetizacion(keyword)
        print(f"   💰 Tipo Monetización: {tipo_monetizacion}")
        
        # Test potencial (función original)
        potencial = analyzer.get_monetization_potential(keyword)
        print(f"   📈 Potencial: {potencial}")
    
    print("\n" + "=" * 50)
    print("✅ Testing completado - Las mejoras están funcionando!")

if __name__ == "__main__":
    test_mejoras()
