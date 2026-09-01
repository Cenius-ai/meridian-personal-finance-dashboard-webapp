"""Category catalog for Meridian.

Colors are chosen for legibility on the near-black dashboard surface while
keeping the Meridian vermilion accent reserved for the Food category (the
most frequent spending bucket). Chart libraries receive these hex values
directly; never oklch() strings.
"""

CATEGORIES = [
    {
        "id": 1,
        "name": "Food",
        "color": "#ed7940",
        "description": "Groceries, restaurants, coffee, and takeout",
    },
    {
        "id": 2,
        "name": "Housing",
        "color": "#4f8fdf",
        "description": "Rent, insurance, and home services",
    },
    {
        "id": 3,
        "name": "Transportation",
        "color": "#45b7a4",
        "description": "Fuel, transit, rideshare, and parking",
    },
    {
        "id": 4,
        "name": "Entertainment",
        "color": "#b07ce8",
        "description": "Streaming, events, games, and media",
    },
    {
        "id": 5,
        "name": "Utilities",
        "color": "#e0b64a",
        "description": "Electric, internet, phone, and water",
    },
    {
        "id": 6,
        "name": "Shopping",
        "color": "#e0647f",
        "description": "Retail, clothing, home, and electronics",
    },
    {
        "id": 7,
        "name": "Healthcare",
        "color": "#58b86a",
        "description": "Pharmacy, dental, and medical visits",
    },
    {
        "id": 8,
        "name": "Travel",
        "color": "#6f7bd6",
        "description": "Flights, lodging, rail, and rental cars",
    },
]

CATEGORY_BY_NAME = {c["name"]: c for c in CATEGORIES}
CATEGORY_BY_ID = {c["id"]: c for c in CATEGORIES}
CATEGORY_NAMES = [c["name"] for c in CATEGORIES]
