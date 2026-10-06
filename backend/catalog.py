"""Ten campus aisles for the sponsored-label study.

Each aisle has nine products. The target is the median-priced item and is
always placed in the first slot (top-left). Only the label changes.
"""

CATEGORIES = [
    {
        "key": "snacks",
        "title": "Snack aisle",
        "blurb": "Something for the walk between classes.",
        "budget": 12,
        "accent": "#e09a3e",
        "products": [
            {"id": "snack-chews", "name": "Fruit chews", "price": 1.25, "unit": "2 oz bag", "detail": "Soft little candies that disappear during a lecture.", "target": False},
            {"id": "snack-bar", "name": "Honey oat bar", "price": 1.75, "unit": "1 bar", "detail": "A chewy oat bar that survives a backpack.", "target": False},
            {"id": "snack-pretzels", "name": "Salted pretzels", "price": 2.25, "unit": "5 oz bag", "detail": "Salty twists for a study break.", "target": False},
            {"id": "snack-chips", "name": "Kettle chips", "price": 2.75, "unit": "5 oz bag", "detail": "Thick-cut chips with a little crunch and salt.", "target": False},
            {"id": "snack-cookie", "name": "Chocolate protein cookie", "price": 3.50, "unit": "1 cookie", "detail": "Soft-baked, with enough protein to feel practical.", "target": True},
            {"id": "snack-chocolate", "name": "Dark chocolate bar", "price": 4.00, "unit": "2.5 oz", "detail": "A slow bar, not a candy you finish in the checkout line.", "target": False},
            {"id": "snack-popcorn", "name": "Cheddar popcorn", "price": 4.75, "unit": "tin", "detail": "A shareable tin that usually gets finished the same night.", "target": False},
            {"id": "snack-nuts", "name": "Roasted mixed nuts", "price": 5.50, "unit": "8 oz", "detail": "A heartier bag for long library afternoons.", "target": False},
            {"id": "snack-jerky", "name": "Pepper beef jerky", "price": 6.25, "unit": "3 oz", "detail": "Savory and filling when you skip a meal.", "target": False},
        ],
    },
    {
        "key": "dorm",
        "title": "Dorm essentials",
        "blurb": "The room still needs a few basics.",
        "budget": 32,
        "accent": "#7d9a78",
        "products": [
            {"id": "dorm-hooks", "name": "Adhesive hooks", "price": 4.00, "unit": "4 pack", "detail": "For towels, totes, and the jacket that never finds a chair.", "target": False},
            {"id": "dorm-bags", "name": "Small trash bags", "price": 5.50, "unit": "20 count", "detail": "The unglamorous pack you only notice when it runs out.", "target": False},
            {"id": "dorm-caddy", "name": "Shower caddy", "price": 7.00, "unit": "1 caddy", "detail": "Carries soap down the hall without a juggling act.", "target": False},
            {"id": "dorm-hangers", "name": "Slim hangers", "price": 8.50, "unit": "10 pack", "detail": "Enough hangers to get a pile of clothes off the bed.", "target": False},
            {"id": "dorm-hamper", "name": "Collapsible hamper", "price": 12.00, "unit": "1 hamper", "detail": "Stands in a corner and folds flat at the end of term.", "target": True},
            {"id": "dorm-lamp", "name": "Clip-on lamp", "price": 15.00, "unit": "1 lamp", "detail": "Clips to a lofted bed when the ceiling light is too much.", "target": False},
            {"id": "dorm-throw", "name": "Fleece throw", "price": 18.00, "unit": "1 throw", "detail": "A warm layer for a cold room and a colder couch.", "target": False},
            {"id": "dorm-cubes", "name": "Fabric storage cubes", "price": 22.00, "unit": "set of 2", "detail": "Hides snacks, chargers, and the off-season hoodie.", "target": False},
            {"id": "dorm-topper", "name": "Twin foam topper", "price": 28.00, "unit": "twin", "detail": "Takes the edge off a standard dorm mattress.", "target": False},
        ],
    },
    {
        "key": "tech",
        "title": "Tech accessories",
        "blurb": "Small gear that makes a laptop setup less annoying.",
        "budget": 45,
        "accent": "#6a8caf",
        "products": [
            {"id": "tech-clips", "name": "Cable clips", "price": 5.00, "unit": "6 pack", "detail": "Keeps charging cords from sliding off the desk.", "target": False},
            {"id": "tech-cloth", "name": "Screen cloth", "price": 6.00, "unit": "2 cloths", "detail": "A soft cloth for fingerprints on a laptop screen.", "target": False},
            {"id": "tech-stand", "name": "Phone stand", "price": 9.00, "unit": "1 stand", "detail": "Props a phone up for a recipe or a lecture recording.", "target": False},
            {"id": "tech-cable", "name": "USB-C cable", "price": 12.00, "unit": "6 ft", "detail": "A longer cable so the outlet is not under the pillow.", "target": False},
            {"id": "tech-mouse", "name": "Compact mouse", "price": 18.00, "unit": "wireless", "detail": "A small silent mouse for library tables and long papers.", "target": True},
            {"id": "tech-bank", "name": "Power bank", "price": 22.00, "unit": "10,000 mAh", "detail": "A full phone charge, plus a little left for the ride home.", "target": False},
            {"id": "tech-riser", "name": "Laptop stand", "price": 27.00, "unit": "folding", "detail": "Lifts the screen so you are not hunched over a seminar.", "target": False},
            {"id": "tech-keypad", "name": "Compact keypad", "price": 34.00, "unit": "bluetooth", "detail": "A short keyboard when the laptop keys feel cramped.", "target": False},
            {"id": "tech-earbuds", "name": "Wireless earbuds", "price": 40.00, "unit": "with case", "detail": "For walks, problem sets, and roommates who have guests.", "target": False},
        ],
    },
    {
        "key": "drinks",
        "title": "Drink cooler",
        "blurb": "Grab a drink before the next block.",
        "budget": 11,
        "accent": "#3f8f9a",
        "products": [
            {"id": "drink-water", "name": "Still water", "price": 1.25, "unit": "16 oz", "detail": "Plain cold water. The reliable choice.", "target": False},
            {"id": "drink-tea", "name": "Bottled tea", "price": 1.75, "unit": "16 oz", "detail": "Lightly sweet iced tea.", "target": False},
            {"id": "drink-cola", "name": "Cola", "price": 2.00, "unit": "12 oz", "detail": "Cold, fizzy, and familiar.", "target": False},
            {"id": "drink-sparkling", "name": "Sparkling water", "price": 2.50, "unit": "12 oz", "detail": "Unsweetened bubbles with a lime note.", "target": False},
            {"id": "drink-coldbrew", "name": "Cold brew", "price": 3.75, "unit": "10 oz", "detail": "Smooth coffee for an 8 a.m. that should have been later.", "target": True},
            {"id": "drink-energy", "name": "Energy drink", "price": 4.25, "unit": "12 oz", "detail": "A brighter, sweeter kick than coffee.", "target": False},
            {"id": "drink-smoothie", "name": "Berry smoothie", "price": 4.75, "unit": "12 oz", "detail": "Thick and filling enough to pass for breakfast.", "target": False},
            {"id": "drink-kombucha", "name": "Ginger kombucha", "price": 5.25, "unit": "14 oz", "detail": "Tart, fizzy, and a little spicy.", "target": False},
            {"id": "drink-juice", "name": "Fresh orange juice", "price": 5.75, "unit": "12 oz", "detail": "Pressed juice, not from a carton in the back.", "target": False},
        ],
    },
    {
        "key": "school",
        "title": "School supplies",
        "blurb": "Restock the bag before the week gets away.",
        "budget": 20,
        "accent": "#c47b4a",
        "products": [
            {"id": "school-pencils", "name": "Pencil pack", "price": 1.50, "unit": "8 pencils", "detail": "A simple pack that always goes missing one by one.", "target": False},
            {"id": "school-highlighters", "name": "Highlighters", "price": 2.75, "unit": "4 colors", "detail": "Yellow, pink, green, and blue for a dense reading.", "target": False},
            {"id": "school-notes", "name": "Sticky notes", "price": 3.50, "unit": "4 pads", "detail": "For flags in a textbook you would rather not write in.", "target": False},
            {"id": "school-notebooks", "name": "Notebook three-pack", "price": 5.00, "unit": "3 notebooks", "detail": "One for each class that still wants paper.", "target": False},
            {"id": "school-planner", "name": "Weekly planner", "price": 7.50, "unit": "semester", "detail": "A paper week-view for due dates that get lost in a phone.", "target": True},
            {"id": "school-binder", "name": "One-inch binder", "price": 9.00, "unit": "1 binder", "detail": "Holds a unit's worth of handouts without becoming a brick.", "target": False},
            {"id": "school-pens", "name": "Gel pen set", "price": 10.50, "unit": "6 pens", "detail": "Smooth black and colored pens for notes you might reread.", "target": False},
            {"id": "school-folders", "name": "Folder bundle", "price": 12.00, "unit": "8 folders", "detail": "A color for each class, if the system survives October.", "target": False},
            {"id": "school-calculator", "name": "Scientific calculator", "price": 16.00, "unit": "1 calculator", "detail": "Allowed in the exams that ban a phone.", "target": False},
        ],
    },
    {
        "key": "care",
        "title": "Personal care",
        "blurb": "The toiletry shelf is looking thin.",
        "budget": 18,
        "accent": "#c47d8a",
        "products": [
            {"id": "care-balm", "name": "Lip balm", "price": 2.00, "unit": "1 stick", "detail": "Unscented, for windy walks across the quad.", "target": False},
            {"id": "care-soap", "name": "Hand soap", "price": 3.00, "unit": "8 oz", "detail": "A small bottle that fits on a dorm sink.", "target": False},
            {"id": "care-brush", "name": "Toothbrush", "price": 3.50, "unit": "1 brush", "detail": "A replacement for the one that should have been retired.", "target": False},
            {"id": "care-deodorant", "name": "Deodorant", "price": 4.50, "unit": "1 stick", "detail": "A regular stick for everyday classes.", "target": False},
            {"id": "care-wipes", "name": "Face wipes", "price": 6.50, "unit": "30 count", "detail": "Useful when you will not make it to a real sink.", "target": True},
            {"id": "care-shampoo", "name": "Shampoo", "price": 8.00, "unit": "12 oz", "detail": "A mid-size bottle for a shared shower.", "target": False},
            {"id": "care-lotion", "name": "Daily lotion", "price": 9.00, "unit": "8 oz", "detail": "Light lotion for dry heated rooms.", "target": False},
            {"id": "care-sunscreen", "name": "Face sunscreen", "price": 11.00, "unit": "1.7 oz", "detail": "Does not leave a white cast under a backpack strap.", "target": False},
            {"id": "care-mask", "name": "Hair mask", "price": 13.00, "unit": "6 oz", "detail": "A richer treatment for the week the weather turns.", "target": False},
        ],
    },
    {
        "key": "desk",
        "title": "Desk setup",
        "blurb": "Make the desk somewhere you actually sit.",
        "budget": 36,
        "accent": "#b08968",
        "products": [
            {"id": "desk-cup", "name": "Pen cup", "price": 5.00, "unit": "ceramic", "detail": "A heavy cup so pens stop rolling into the radiator.", "target": False},
            {"id": "desk-coasters", "name": "Coaster set", "price": 6.00, "unit": "4 coasters", "detail": "Saves the desk from a semester of coffee rings.", "target": False},
            {"id": "desk-pad", "name": "Mouse pad", "price": 8.00, "unit": "standard", "detail": "A plain pad with a stitched edge.", "target": False},
            {"id": "desk-plant", "name": "Mini desk plant", "price": 11.00, "unit": "in pot", "detail": "A small hardy plant that tolerates missed waterings.", "target": False},
            {"id": "desk-lamp", "name": "LED desk lamp", "price": 16.00, "unit": "dimmable", "detail": "A warm lamp with a dimmer for late writing.", "target": True},
            {"id": "desk-riser", "name": "Monitor riser", "price": 21.00, "unit": "bamboo", "detail": "Lifts a screen and leaves a shelf underneath for a notebook.", "target": False},
            {"id": "desk-cork", "name": "Cork board", "price": 24.00, "unit": "17 x 23 in", "detail": "For deadlines, tickets, and the one photo you printed.", "target": False},
            {"id": "desk-speaker", "name": "Desktop speaker", "price": 29.00, "unit": "single", "detail": "A small speaker for music while you clean or draft.", "target": False},
            {"id": "desk-tray", "name": "Keyboard tray", "price": 34.00, "unit": "clamp-on", "detail": "Pulls the keyboard closer when the desk is too high.", "target": False},
        ],
    },
    {
        "key": "kitchen",
        "title": "Mini kitchen",
        "blurb": "Stock the corner that passes for a kitchen.",
        "budget": 24,
        "accent": "#d07a4c",
        "products": [
            {"id": "kitchen-mug", "name": "Ceramic mug", "price": 4.00, "unit": "12 oz", "detail": "A sturdy mug that can live on a bookshelf.", "target": False},
            {"id": "kitchen-soap", "name": "Dish soap", "price": 4.50, "unit": "8 oz", "detail": "Enough for a sink that is usually a mug and a spoon.", "target": False},
            {"id": "kitchen-oatmeal", "name": "Oatmeal cups", "price": 5.50, "unit": "6 cups", "detail": "Add hot water. Breakfast when the dining hall is closed.", "target": False},
            {"id": "kitchen-mac", "name": "Mac and cheese cups", "price": 6.50, "unit": "4 cups", "detail": "The late-night version of a real meal.", "target": False},
            {"id": "kitchen-ramen", "name": "Ramen variety pack", "price": 9.00, "unit": "6 bowls", "detail": "A mix of flavors so dinner is not the same bowl every time.", "target": True},
            {"id": "kitchen-coffee", "name": "Coffee bag", "price": 11.00, "unit": "12 oz", "detail": "Ground coffee for a French press or a cheap drip cone.", "target": False},
            {"id": "kitchen-skillet", "name": "Mini skillet", "price": 14.00, "unit": "6 inch", "detail": "Big enough for an egg or a grilled cheese.", "target": False},
            {"id": "kitchen-press", "name": "French press", "price": 17.00, "unit": "3 cup", "detail": "Coffee without a machine you have to hide at inspection.", "target": False},
            {"id": "kitchen-kettle", "name": "Electric kettle", "price": 22.00, "unit": "1 liter", "detail": "Boils water for oatmeal, tea, and the ramen pack.", "target": False},
        ],
    },
    {
        "key": "fitness",
        "title": "Fitness corner",
        "blurb": "A little gear for a room workout.",
        "budget": 30,
        "accent": "#5e8f6a",
        "products": [
            {"id": "fit-band", "name": "Resistance band", "price": 6.00, "unit": "medium", "detail": "A loop band for short workouts between classes.", "target": False},
            {"id": "fit-rope", "name": "Jump rope", "price": 8.00, "unit": "adjustable", "detail": "Folds into a drawer. Needs more ceiling than you think.", "target": False},
            {"id": "fit-bottle", "name": "Sports bottle", "price": 10.00, "unit": "24 oz", "detail": "A leak-resistant bottle that fits a side pocket.", "target": False},
            {"id": "fit-towel", "name": "Sweat towel", "price": 12.00, "unit": "gym size", "detail": "Thicker than a shower towel and easier to wash.", "target": False},
            {"id": "fit-mat", "name": "Yoga mat", "price": 16.00, "unit": "standard", "detail": "Enough cushion for a floor that is basically concrete.", "target": True},
            {"id": "fit-bell", "name": "Kettlebell", "price": 19.00, "unit": "10 lb", "detail": "One bell, a lot of swings, not much storage.", "target": False},
            {"id": "fit-roller", "name": "Foam roller", "price": 23.00, "unit": "18 inch", "detail": "For sore legs after you suddenly start running again.", "target": False},
            {"id": "fit-weights", "name": "Ankle weights", "price": 26.00, "unit": "pair", "detail": "Strap-on weights for walks and slow lifts.", "target": False},
            {"id": "fit-bag", "name": "Gym bag", "price": 29.00, "unit": "duffel", "detail": "A separate bag so the backpack does not smell like the gym.", "target": False},
        ],
    },
    {
        "key": "fun",
        "title": "Downtime",
        "blurb": "Something that is not for a class.",
        "budget": 22,
        "accent": "#8b74a8",
        "products": [
            {"id": "fun-puzzle", "name": "Mini puzzle", "price": 4.50, "unit": "150 pieces", "detail": "A short puzzle for a Sunday that got rained out.", "target": False},
            {"id": "fun-cards", "name": "Card game", "price": 6.00, "unit": "travel deck", "detail": "A compact game that comes out when friends visit.", "target": False},
            {"id": "fun-magazine", "name": "Magazine", "price": 7.00, "unit": "latest issue", "detail": "Something to read that will not be on the exam.", "target": False},
            {"id": "fun-book", "name": "Paperback novel", "price": 9.50, "unit": "1 book", "detail": "A novel picked for the evening, not the syllabus.", "target": False},
            {"id": "fun-candle", "name": "Soy candle", "price": 11.00, "unit": "8 oz", "detail": "A mild scent for a room that shares a vent.", "target": True},
            {"id": "fun-sketch", "name": "Sketchbook", "price": 13.50, "unit": "80 pages", "detail": "Blank paper for doodles that are not design homework.", "target": False},
            {"id": "fun-board", "name": "Small board game", "price": 16.00, "unit": "2–4 players", "detail": "A short game that fits on a dorm desk.", "target": False},
            {"id": "fun-mic", "name": "Karaoke mic", "price": 18.50, "unit": "wired", "detail": "A wired mic for singing along when the room is empty.", "target": False},
            {"id": "fun-speaker", "name": "Mini speaker", "price": 21.00, "unit": "bluetooth", "detail": "A palm-sized speaker for playlists and calls.", "target": False},
        ],
    },
]


def assert_catalog():
    ids = []
    keys = set()
    if not 8 <= len(CATEGORIES) <= 10:
        raise RuntimeError("The study needs 8 to 10 aisles.")
    for category in CATEGORIES:
        if category["key"] in keys:
            raise RuntimeError(f"Duplicate aisle {category['key']}.")
        keys.add(category["key"])
        products = category["products"]
        if not 6 <= len(products) <= 9:
            raise RuntimeError(f"{category['key']} should have 6 to 9 products.")
        required = ("id", "name", "price", "unit", "detail")
        for product in products:
            for field in required:
                if not product.get(field) and product.get(field) != 0:
                    raise RuntimeError(f"{category['key']} is missing {field}.")
            if isinstance(product["price"], bool) or not isinstance(product["price"], (int, float)):
                raise RuntimeError(f"{product['id']} has a bad price.")
            if product["price"] <= 0:
                raise RuntimeError(f"{product['id']} must cost something.")
        targets = [product for product in products if product.get("target")]
        if len(targets) != 1:
            raise RuntimeError(f"{category['key']} needs exactly one target product.")
        prices = sorted(int(round(product["price"] * 100)) for product in products)
        target_cents = int(round(targets[0]["price"] * 100))
        if target_cents != prices[len(prices) // 2]:
            raise RuntimeError(f"{category['key']} target should be the median-priced item.")
        budget = category["budget"]
        if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget <= 0:
            raise RuntimeError(f"{category['key']} needs a budget.")
        budget_cents = int(round(budget * 100))
        if budget_cents < prices[-1]:
            raise RuntimeError(f"{category['key']} budget cannot afford every single item.")
        if budget_cents < target_cents + prices[0]:
            raise RuntimeError(f"{category['key']} budget cannot afford the target plus a cheaper item.")
        if budget_cents >= sum(prices):
            raise RuntimeError(f"{category['key']} budget can buy the whole aisle.")
        local_ids = [product["id"] for product in products]
        if len(local_ids) != len(set(local_ids)):
            raise RuntimeError(f"{category['key']} repeats a product id.")
        ids.extend(local_ids)
    if len(ids) != len(set(ids)):
        raise RuntimeError("Product ids repeat across aisles.")


assert_catalog()
