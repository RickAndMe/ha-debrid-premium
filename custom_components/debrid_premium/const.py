"""Constantes de Debrid Premium."""

DOMAIN = "debrid_premium"

CONF_SERVICIO = "servicio"
CONF_CLAVE = "clave"

# Se consulta una vez al día: son cuentas que caducan por meses y
# Real-Debrid penaliza el polling agresivo.
INTERVALO = 1440  # minutos
TIMEOUT = 25

SERVICIOS = {
    "realdebrid": {
        "name": "Real-Debrid",
        "url": "https://api.real-debrid.com/rest/1.0/user",
        "account_url": "https://real-debrid.com/account",
        "token_url": "https://real-debrid.com/apitoken",
        "icon": "mdi:crown",
        "puntos": True,
    },
    "alldebrid": {
        "name": "AllDebrid",
        "url": "https://api.alldebrid.com/v4/user?agent=hermes-ha",
        "account_url": "https://alldebrid.com/account/",
        "token_url": "https://alldebrid.com/apikeys/",
        "icon": "mdi:crown",
        "puntos": True,
    },
    "torbox": {
        "name": "TorBox",
        "url": "https://api.torbox.app/v1/api/user/me",
        "account_url": "https://torbox.app/subscription",
        "token_url": "https://torbox.app/settings",
        "icon": "mdi:crown",
        "puntos": False,
    },
}
