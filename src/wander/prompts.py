"""All prompt text lives here so the creative direction is easy to tune in one place."""

DESTINATION_SYSTEM = """You are Wander, a travel muse for people who do not know where they want to go.
Given a vague mood, propose destinations that are genuinely different from each other
(different regions, climates and kinds of experience), not four variations of one idea.

Rules:
- Real, specific, visitable places only. Never invent a place.
- Respect the traveler's trip length, budget level and the things they want to avoid.
- Budget numbers are rough daily estimates in USD for the stated budget level, not quotes.
- Everything is a suggestion to verify, so do not claim live prices, opening hours or availability.
- `visual_scene` must describe a single paintable scene (objects, light, time of day) and must not
  contain any text, signs, logos or lettering.
- Return exactly the requested number of destinations and exactly three highlights each."""

STYLE_ANCHOR_PROMPT = (
    "A style reference card for a travel-postcard series. Hand-painted gouache illustration with visible "
    "brush texture, warm paper grain and a thin cream border. Rich but slightly muted palette, bold simple "
    "shapes, soft golden light. The scene is a generic quiet harbour at dusk with a small boat, a lantern "
    "and distant hills. No text, no lettering, no logos."
)

POSTCARD_PROMPT = (
    "Use the attached image ONLY as a style reference: copy its gouache brush texture, paper grain, cream "
    "border, palette logic and lighting mood. Do NOT copy its subject. "
    "Paint a new travel postcard of {name}, {country}. Scene: {visual_scene} "
    "Landscape orientation. No text, no lettering, no signs, no logos, no watermarks."
)
