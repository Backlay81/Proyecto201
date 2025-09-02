"""
Instrucciones para utilizar la API de Google Ads

1. Completar el archivo de credenciales
------------------------------------------
Edita el archivo `credentials/google-ads.yaml` y completa:

- developer_token: Solicítalo en https://developers.google.com/google-ads/api/docs/first-call/dev-token
- client_id: Ya está rellenado con tu ID
- client_secret: Ya está rellenado con tu secreto
- refresh_token: Necesitas obtenerlo (ver paso 2)
- login_customer_id: Tu ID de cliente de Google Ads (sin guiones)

2. Obtener el refresh_token
------------------------------------------
Para obtener el refresh_token, necesitas ejecutar un script de autenticación
que te dará un enlace para autorizar la aplicación y obtener el token.

Google proporciona un script en Python para hacerlo:
https://github.com/googleads/google-ads-python/blob/master/examples/authentication/authenticate_in_standalone_application.py

3. Pasos para iniciar
------------------------------------------
1. Solicita un developer_token
2. Obtén tu login_customer_id
3. Genera el refresh_token
4. Completa el archivo yaml
5. Ejecuta google_ads_keywords.py para verificar la conexión

4. Próximos pasos
------------------------------------------
Una vez que la conexión funcione, podremos:
- Buscar palabras clave por volumen
- Filtrar por competencia
- Exportar resultados
- Integrar con n8n para automatizar

Notas:
- Guarda tus credenciales seguras
- No compartas el archivo yaml
"""
