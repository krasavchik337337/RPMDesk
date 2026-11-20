import csv
from datetime import datetime
from pathlib import Path
from database import reports_repository
from config import REPORT_NAMES, MOVEMENT_NAMES


def format_date(value):
    if not value:
        return ""

    try:
        date_value = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        return date_value.strftime("%d.%m.%Y %H:%M")

    except ValueError:
        return str(value)


def write_section(writer, title, headers, rows):
    writer.writerow([title])
    writer.writerow(headers)

    for row in rows:
        writer.writerow(row)

    writer.writerow([])


def generate_report(
        report_type,
        date_from,
        date_to,
        output_path,
        customer_id=None,
        vehicle_id=None
):
    if report_type not in REPORT_NAMES:
        raise ValueError("Unknown report type.")

    if report_type != "inventory_balance":
        if not date_from or not date_to:
            raise ValueError("A report period is required.")

        try:
            start_date = datetime.strptime(
                date_from,
                "%Y-%m-%d"
            )

            end_date = datetime.strptime(
                date_to,
                "%Y-%m-%d"
            )

        except ValueError:
            raise ValueError(
                "Dates must use YYYY-MM-DD format."
            )

        if start_date > end_date:
            raise ValueError(
                "The start date cannot be later than the end date."
            )

    output_path = Path(output_path)

    with open(
            output_path,
            "w",
            encoding="utf-8-sig",
            newline=""
    ) as file:

        writer = csv.writer(
            file,
            delimiter=";"
        )

        writer.writerow([REPORT_NAMES[report_type]])
        writer.writerow([
            "Generated:",
            datetime.now().strftime("%d.%m.%Y %H:%M")
        ])

        if report_type != "inventory_balance":
            writer.writerow(["Period:", date_from, "-", date_to])

        writer.writerow([])

        if report_type == "service_history":
            records = reports_repository.get_service_history_report(
                date_from,
                date_to,
                customer_id,
                vehicle_id
            )

            rows = []

            for record in records:
                rows.append([
                    format_date(record["service_date"]),
                    (
                        f'{record["last_name"]} '
                        f'{record["first_name"]}'
                    ),
                    (
                        f'{record["make"]} '
                        f'{record["model"]} '
                        f'{record["year"] or ""}'
                    ).strip(),
                    record["mileage"] or "",
                    record["works"] or "",
                    record["used_parts"] or "",
                    record["notes"] or ""
                ])

            write_section(
                writer,
                "Service history",
                [
                    "Date",
                    "Customer",
                    "Vehicle",
                    "Mileage",
                    "Works",
                    "Used parts",
                    "Notes"
                ],
                rows
            )

        elif report_type == "service_statistics":
            data = reports_repository.get_service_statistics_report(
                date_from,
                date_to,
                customer_id,
                vehicle_id
            )

            summary = data["summary"]

            write_section(
                writer,
                "General statistics",
                ["Metric", "Value"],
                [
                    ["Completed visits", summary["visit_count"]],
                    ["Performed works", summary["work_count"]]
                ]
            )

            write_section(
                writer,
                "Popular works",
                ["Work", "Quantity"],
                [
                    [item["name"], item["quantity"]]
                    for item in data["popular_works"]
                ]
            )

            write_section(
                writer,
                "Service activity",
                ["Month", "Visits"],
                [
                    [item["month"], item["visit_count"]]
                    for item in data["activity"]
                ]
            )

        elif report_type == "inventory_balance":
            items = reports_repository.get_inventory_balance_report()

            rows = []

            for item in items:
                unit = (
                    "pcs"
                    if item["unit"] == "piece"
                    else "ml"
                )

                rows.append([
                    item["name"],
                    item["brand"] or "",
                    item["category"] or "",
                    item["stock"],
                    unit,
                    item["notes"] or ""
                ])

            write_section(
                writer,
                "Inventory balance",
                [
                    "Item",
                    "Brand",
                    "Category",
                    "Quantity",
                    "Unit",
                    "Notes"
                ],
                rows
            )

        elif report_type == "stock_movements":
            records = reports_repository.get_stock_movements_report(
                date_from,
                date_to,
                customer_id,
                vehicle_id
            )

            rows = []

            for item in records:
                unit = (
                    "pcs"
                    if item["unit"] == "piece"
                    else "ml"
                )

                rows.append([
                    format_date(item["created_at"]),
                    item["item_name"],
                    item["category"] or "",
                    MOVEMENT_NAMES.get(
                        item["movement_type"],
                        item["movement_type"]
                    ),
                    item["quantity"],
                    unit,
                    item["service_record_id"] or "",
                    item["note"] or ""
                ])

            write_section(
                writer,
                "Stock movements",
                [
                    "Date",
                    "Item",
                    "Category",
                    "Movement",
                    "Quantity",
                    "Unit",
                    "Service ID",
                    "Notes"
                ],
                rows
            )

    return output_path
