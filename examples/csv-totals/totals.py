"""Sum a CSV amount column exactly using only the standard library."""

import argparse
import csv
from decimal import Decimal, InvalidOperation, localcontext
import json
import sys


def sum_amounts(path):
    """Return the exact sum; reject invalid CSV amounts with line numbers."""
    values = []
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or "amount" not in reader.fieldnames:
            raise ValueError("CSV header must contain amount")
        try:
            for row in reader:
                raw = row.get("amount")
                if raw is None:
                    raise ValueError(f"row {reader.line_num}: missing amount")
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    amount = Decimal(raw)
                except InvalidOperation as exc:
                    raise ValueError(
                        f"row {reader.line_num}: invalid amount {raw!r}"
                    ) from exc
                if not amount.is_finite():
                    raise ValueError(
                        f"row {reader.line_num}: invalid amount {raw!r}"
                    )
                values.append(amount)
        except csv.Error as exc:
            raise ValueError(f"row {reader.line_num}: invalid CSV: {exc}") from exc
    if not values:
        return Decimal(0)
    # Preserve every input digit, including carry digits across all additions.
    smallest_exponent = min(value.as_tuple().exponent for value in values)
    largest_position = max(value.adjusted() for value in values)
    with localcontext() as context:
        context.prec = max(
            1, largest_position - min(smallest_exponent, 0) + len(str(len(values))) + 2
        )
        return sum(values, Decimal(0))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="CSV file with an amount header")
    args = parser.parse_args(argv)
    try:
        total = sum_amounts(args.file)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"total": format(total, "f")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
