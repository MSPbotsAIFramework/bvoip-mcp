from .._json import error_envelope

NO_TOKEN = error_envelope(
    "not_configured", "No Bvoip API key. Send the X-Bvoip-Api-Key header.", False
)
