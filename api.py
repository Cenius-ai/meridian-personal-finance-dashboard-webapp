"""Flask JSON endpoints mounted on the Dash server.

Every endpoint is a thin wrapper around the data layer in
``data.repository``. Responses use a consistent ``{data, page?, error?}``
envelope; invalid inputs return a controlled 400 rather than leaking a stack
trace.
"""

from __future__ import annotations

import logging

from flask import Flask, jsonify, request

from data import repository

log = logging.getLogger("meridian.api")


def _error(message: str, status: int):
    return jsonify({"error": {"message": message, "status": status}}), status


def _month_or_none(value: str | None) -> str | None:
    if value in (None, "", "all"):
        return None
    if value not in repository.ALL_MONTHS:
        raise ValueError("month must be one of YYYY-MM in the seeded range")
    return value


def register(server: Flask) -> None:
    """Attach all JSON endpoints to the given Flask app."""

    @server.get("/api/categories")
    def categories():
        return jsonify({"data": repository.list_categories()})

    @server.get("/api/transactions")
    def transactions():
        try:
            month = _month_or_none(request.args.get("month"))
            category = request.args.get("category") or None
            search = request.args.get("search") or None
            sort_by = request.args.get("sort_by", "date")
            sort_order = request.args.get("sort_order", "desc")

            if sort_by not in ("date", "amount"):
                return _error("sort_by must be 'date' or 'amount'", 400)
            if sort_order not in ("asc", "desc"):
                return _error("sort_order must be 'asc' or 'desc'", 400)

            page_raw = request.args.get("page")
            page_size_raw = request.args.get("page_size", "25")
            try:
                page = int(page_raw) if page_raw is not None else None
                page_size = int(page_size_raw)
            except (TypeError, ValueError):
                return _error("page and page_size must be integers", 400)

            payload = repository.list_transactions(
                month=month,
                category=category,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
                page=page,
                page_size=page_size,
            )
            return jsonify(payload)
        except ValueError as exc:
            return _error(str(exc), 400)

    @server.get("/api/spending-by-category")
    def spending_by_category():
        try:
            month = _month_or_none(request.args.get("month"))
        except ValueError as exc:
            return _error(str(exc), 400)

        if month is None:
            return _error("a 'month' query parameter is required", 400)

        rows = repository.spending_by_category(month)
        monthly_total = sum(row["total_cents"] for row in rows)
        return jsonify({"data": rows, "month": month, "monthly_total_cents": monthly_total})

    @server.get("/api/category-trend")
    def category_trend():
        category = request.args.get("category") or None
        months_raw = request.args.get("months", "12")
        try:
            months = int(months_raw)
        except (TypeError, ValueError):
            return _error("months must be an integer", 400)

        if not category:
            return _error("a 'category' query parameter is required", 400)
        if category not in repository.CATEGORY_NAMES:
            return _error("unknown category", 400)

        rows = repository.category_trend(category, months=months)
        return jsonify({"data": rows, "category": category})
