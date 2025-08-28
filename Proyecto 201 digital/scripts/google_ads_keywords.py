"""
Script básico para consultar palabras clave en Google Ads API.
Autor: Proyecto 201 digital
Fecha: 27/08/2025
"""

import sys
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def main():
    print("Conectando con Google Ads API...")
    yaml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials", "google-ads.yaml")
    if not os.path.exists(yaml_path):
        print(f"Error: No se encontró el archivo de configuración en {yaml_path}")
        return
    try:
        client = GoogleAdsClient.load_from_storage(yaml_path)
        print("✅ Conexión establecida con éxito!")

        # Parámetros de búsqueda
        customer_id = str(client.login_customer_id or os.getenv('GOOGLE_ADS_CUSTOMER_ID'))
        if not customer_id:
            print("No se ha encontrado el login_customer_id. Configúralo en google-ads.yaml.")
            return

        # Palabra semilla para buscar ideas
        keyword_seed = "marketing digital"
        location_id = "2840"  # España
        language_id = "1000"  # Español

        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
        keyword_competition_level_enum = client.enums.KeywordPlanCompetitionLevelEnum

        # Construir la petición
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = f"languages/{language_id}"
        request.geo_target_constants.append(f"geoTargetConstants/{location_id}")
        request.keyword_seed.keywords.append(keyword_seed)

        print(f"Buscando ideas de palabras clave para: '{keyword_seed}'...")
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

        print("\nResultados:")
        for idea in response:
            print(f"Palabra clave: {idea.text}")
            print(f"  Volumen de búsquedas mensuales: {idea.keyword_idea_metrics.avg_monthly_searches}")
            print(f"  Competencia: {keyword_competition_level_enum.Name(idea.keyword_idea_metrics.competition)}")
            print("-")

    except GoogleAdsException as ex:
        print(f"Error al conectar con Google Ads: {ex}")
        for error in ex.failure.errors:
            print(f"\tError: {error.message}")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tEn el campo: {field_path_element.field_name}")
    except Exception as ex:
        print(f"Error inesperado: {ex}")

if __name__ == "__main__":
    main()
