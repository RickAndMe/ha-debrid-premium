# Debrid Premium para Home Assistant

Saber de un vistazo si tus cuentas debrid siguen siendo premium y **hasta cuándo**,
sin entrar en la web de cada servicio.

Cada servicio se configura **por separado** y crea **su propio dispositivo** con sus
entidades. Puedes tener Real-Debrid sin AllDebrid, o los tres, y quitarlos de uno en uno.

## Instalación

1. HACS → Integraciones → menú → **Repositorios personalizados**.
2. Añade `https://github.com/RickAndMe/ha-debrid-premium` como **Integration**.
3. Instálala y reinicia Home Assistant.
4. Ajustes → Dispositivos y servicios → **Añadir integración** → «Debrid Premium».
5. Elige el servicio y pega su clave. Repite para los demás.

## Entidades

Un dispositivo por servicio, con:

| Entidad | Qué es |
|---|---|
| **Premium** | Binario: la cuenta está activa ahora mismo |
| **Días que quedan** | Días hasta la caducidad |
| **Caduca el** | Fecha exacta |
| **Puntos de fidelidad** | Solo Real-Debrid y AllDebrid |

El binario lleva como atributos el tipo de cuenta (premium / suscripción / prueba / gratis)
y la fecha de caducidad, útil para automatizaciones.

## Dónde sacar la clave

- **Real-Debrid** → https://real-debrid.com/apitoken (*Create new app token*)
- **AllDebrid** → https://alldebrid.com/apikeys/
- **TorBox** → https://torbox.app/settings (sección API)

## Aviso antes de que caduque

```yaml
trigger:
  - platform: numeric_state
    entity_id: sensor.real_debrid_dias_que_quedan
    below: 7
action:
  - service: notify.send_message
    target:
      entity_id: notify.iphone
    data:
      message: "Real-Debrid caduca en {{ states('sensor.real_debrid_dias_que_quedan') }} días"
```

## Detalles

- Consulta **una vez al día**: las cuentas caducan por meses y Real-Debrid penaliza el
  polling agresivo.
- Si la API falla o rechaza la clave, las entidades de ese servicio pasan a
  `unavailable`; los demás servicios no se ven afectados.
- La clave se valida contra la API al introducirla, así que no se guarda una clave mala.

## Licencia

MIT
