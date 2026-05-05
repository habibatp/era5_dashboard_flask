import ee
from flask import current_app

_EE_INITIALIZED = False

def init_earth_engine():
    global _EE_INITIALIZED

    if _EE_INITIALIZED:
        return

    project_id = current_app.config["EE_PROJECT_ID"]
    service_account = current_app.config.get("EE_SERVICE_ACCOUNT", "")
    private_key_file = current_app.config.get("EE_PRIVATE_KEY_FILE", "")

    try:
        if service_account and private_key_file:
            credentials = ee.ServiceAccountCredentials(service_account, private_key_file)
            ee.Initialize(credentials, project=project_id)
        else:
            # Utilise l'auth déjà configurée localement
            ee.Initialize(project=project_id)

        _EE_INITIALIZED = True
        current_app.logger.info("Earth Engine initialized successfully.")
    except Exception as e:
        current_app.logger.exception("Failed to initialize Earth Engine.")
        raise RuntimeError(f"Earth Engine initialization failed: {e}")