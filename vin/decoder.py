import json
from urllib.error import URLError, HTTPError
from urllib.parse import quote
from urllib.request import urlopen, Request
from config import PLAN_PARTS_TOKEN

NHTSA_URL = (
    "https://vpic.nhtsa.dot.gov/api/vehicles/"
    "DecodeVinValuesExtended/{}?format=json"
)
WENMAR_URL = "https://open.wenmarpro.com/v1/vin/{}"
DBVIN_URL = "https://db.vin/api/v1/vin/{}"


def request_json(url, headers=None):
    request = Request(url, headers=headers or {})

    try:
        with urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    except HTTPError as error:
        raise RuntimeError(f"HTTP {error.code}") from error

    except (URLError, TimeoutError) as error:
        raise RuntimeError("Ошибка подключения к API.") from error

    except json.JSONDecodeError as error:
        raise RuntimeError("API вернул некорректный JSON.") from error


def decode_nhtsa(vin):
    url = NHTSA_URL.format(quote(vin))
    data = request_json(url)

    results = data.get("Results", [])

    if not results:
        raise RuntimeError("NHTSA не вернул данные.")

    result = results[0]

    make = str(result.get("Make") or "").strip()
    model = str(result.get("Model") or "").strip()

    if not make and not model:
        raise RuntimeError("NHTSA не определил автомобиль.")

    year_value = str(result.get("ModelYear") or "").strip()
    year = int(year_value) if year_value.isdigit() else None

    engine_parts = []

    engine_model = str(result.get("EngineModel") or "").strip()
    displacement = str(result.get("DisplacementL") or "").strip()
    fuel = str(result.get("FuelTypePrimary") or "").strip()

    if engine_model:
        engine_parts.append(engine_model)

    if displacement:
        engine_parts.append(f"{displacement} L")

    if fuel:
        engine_parts.append(fuel)

    excluded_fields = {
        "VIN",
        "Make",
        "Model",
        "ModelYear",
        "EngineModel",
        "DisplacementL",
        "FuelTypePrimary"
    }

    additional_data = []

    for key, value in result.items():
        if key in excluded_fields or value is None:
            continue

        value = str(value).strip()

        if not value or value in {"Not Applicable", "0"}:
            continue

        additional_data.append(f"{key}: {value}")

    return {
        "make": make,
        "model": model,
        "year": year,
        "engine": ", ".join(engine_parts),
        "additional_data": "\n".join(additional_data)
    }


def decode_wenmar(vin):
    url = WENMAR_URL.format(quote(vin))
    data = request_json(url)

    make = str(data.get("make") or "").strip()
    model = str(data.get("model") or "").strip()

    if not make and not model:
        raise RuntimeError("Wenmar не определил автомобиль.")

    year_value = str(data.get("year") or "").strip()
    year = int(year_value) if year_value.isdigit() else None

    engine_data = data.get("engine")
    engine = ""

    if isinstance(engine_data, dict):
        engine = str(engine_data.get("label") or "").strip()

        if not engine:
            engine_parts = []

            for key in ("displacement", "cylinders", "hp"):
                value = engine_data.get(key)

                if value is not None:
                    engine_parts.append(str(value))

            engine = ", ".join(engine_parts)

    elif engine_data is not None:
        engine = str(engine_data).strip()

    additional_data = []

    trim = data.get("trim")
    if trim:
        additional_data.append(f"Комплектация: {trim}")

    warnings = data.get("warnings")
    if warnings:
        additional_data.append(f"Предупреждения: {warnings}")

    return {
        "make": make,
        "model": model,
        "year": year,
        "engine": engine,
        "additional_data": "\n".join(additional_data)
    }


def decode_dbvin(vin):
    url = DBVIN_URL.format(quote(vin))
    data = request_json(url)

    make = str(data.get("brand") or "").strip()
    model = str(data.get("model") or "").strip()

    if not make and not model:
        raise RuntimeError("DB.VIN не определил автомобиль.")

    year_value = str(data.get("year") or "").strip()
    year = int(year_value) if year_value.isdigit() else None

    additional_data = []

    fields = {
        "version": "Версия",
        "fuelType": "Тип топлива",
        "bodyType": "Тип кузова",
        "registrationCountry": "Страна регистрации"
    }

    for key, label in fields.items():
        value = data.get(key)

        if value:
            additional_data.append(f"{label}: {value}")

    return {
        "make": make,
        "model": model,
        "year": year,
        "engine": "",
        "additional_data": "\n".join(additional_data)
    }


def decode_plan_parts(vin):
    if not PLAN_PARTS_TOKEN:
        raise RuntimeError("Не указан API-ключ plan.parts.")

    url = f"https://cdn.plan.parts/api/v1/vin/{quote(vin)}"

    headers = {
        "Authorization": f"Bearer {PLAN_PARTS_TOKEN}",
        "Accept": "application/json"
    }

    data = request_json(url, headers)

    if not isinstance(data, dict):
        raise RuntimeError("Некорректный ответ plan.parts.")

    if data.get("success") is False:
        raise RuntimeError("plan.parts не смог расшифровать VIN.")

    vehicle = data.get("vehicle") or {}

    if not isinstance(vehicle, dict):
        vehicle_name = str(vehicle).strip()
        vehicle = {}

    else:
        vehicle_name = ""

    make = str(
        vehicle.get("manufacturer")
        or vehicle.get("brand")
        or vehicle.get("make")
        or data.get("manufacturer")
        or data.get("brand")
        or ""
    ).strip()

    model = str(
        vehicle.get("model")
        or vehicle.get("model_series")
        or data.get("model")
        or vehicle_name
        or ""
    ).strip()

    year_value = (
            vehicle.get("year")
            or data.get("year")
    )

    year = (
        int(year_value)
        if str(year_value or "").isdigit()
        else None
    )

    engine = str(
        vehicle.get("engine")
        or vehicle.get("modification")
        or data.get("engine")
        or ""
    ).strip()

    if not make and not model:
        raise RuntimeError(
            "plan.parts не вернул название автомобиля."
        )

    additional_data = []

    if vehicle_name:
        additional_data.append(
            f"Автомобиль: {vehicle_name}"
        )

    identifiers = {
        "manu_id": "ID производителя",
        "model_id": "ID модели",
        "car_id": "ID автомобиля",
        "ktype": "K-Type"
    }

    for key, label in identifiers.items():
        value = data.get(key) or vehicle.get(key)

        if value is not None:
            additional_data.append(f"{label}: {value}")

    return {
        "make": make,
        "model": model,
        "year": year,
        "engine": engine,
        "additional_data": "\n".join(additional_data)
    }


def decode_vin(vin):
    vin = vin.strip().upper()

    if len(vin) != 17:
        raise ValueError("VIN должен содержать 17 символов.")

    if any(char in vin for char in "IOQ"):
        raise ValueError("VIN не может содержать буквы I, O и Q.")

    services = [
        ("NHTSA", decode_nhtsa),
        ("Wenmar Open", decode_wenmar),
        ("DB.VIN", decode_dbvin),
        ("plan.parts", decode_plan_parts)
    ]

    errors = []

    for service_name, decode_function in services:
        try:
            result = decode_function(vin)
            result["additional_data"] = (
                    f"Источник данных: {service_name}\n"
                    + result["additional_data"]
            )
            return result

        except Exception as error:
            errors.append(f"{service_name}: {error}")
    raise RuntimeError(
        "Не удалось расшифровать VIN ни одним сервисом.\n\n"
        + "\n".join(errors)
    )
