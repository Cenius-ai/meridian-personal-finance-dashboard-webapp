# Usage

Meridian ships with 600 read-only demo transactions so every screen is
populated on first paint. No login is required.

## Overview (`/overview`)

- The **month selector** defaults to June 2024, the latest full month.
- The **KPI strip** shows total spend, transaction count, average, and top
  category for the selected month.
- The **horizontal bar chart** lists category spend descending, with dollar
  labels and a hover tooltip showing transaction count and average.
- **Recent transactions** previews the newest eight rows for the month.

Changing the month updates the chart, KPIs, and preview together.

## Transactions (`/transactions`)

- **Search** matches merchant names and notes (case-insensitive).
- **Month** and **Category** filters narrow the table.
- Column headers for **Date** and **Amount** sort on click (ascending, then
  descending on the next click).
- The table paginates 25 rows per page and shows the total row count.
- **Clear filters** resets search and both dropdowns.
- An empty result set shows a reset action.

## Categories (`/categories`)

- The **category selector** defaults to Food.
- The **trend line** shows 12 months of monthly totals with a dotted average
  reference line.
- The summary strip shows 12-month total, monthly average, and count.
- A filtered **transactions table** lists that category's rows.

## JSON API

All endpoints are read-only and mounted on the same server:

```bash
curl 'http://localhost:8050/api/spending-by-category?month=2024-06'
curl 'http://localhost:8050/api/transactions?month=2024-06&category=Food&page=1&page_size=25'
curl 'http://localhost:8050/api/category-trend?category=Food&months=6'
```

Money is always returned as **integer cents** (`amount_cents` / `total_cents`)
plus a display-formatted `amount` string. No floating-point money is stored or
summed.
