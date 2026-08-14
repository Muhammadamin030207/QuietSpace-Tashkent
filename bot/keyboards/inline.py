from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from config import MINIAPP_URL

LANGUAGES = [
    ("🇺🇿 O'zbekcha", "uz"),
    ("🇷🇺 Русский", "ru"),
    ("🇬🇧 English", "en"),
]


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=f"lang:{code})")] for t, code in LANGUAGES
        ]
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📍 Joylashuv orqali qidirish", request_location=True),
                KeyboardButton(text="🎛 Filtr bilan qidirish"),
            ],
            [
                KeyboardButton(text="🤖 AI bilan so'rash"),
                KeyboardButton(text="⭐ Sevimlilar"),
            ],
            [KeyboardButton(text="🌐 Mini App ochish")],
        ],
        resize_keyboard=True,
    )


def mini_app_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Mini App ochish", web_app=WebAppInfo(url=MINIAPP_URL))]
        ]
    )


CATEGORY_OPTIONS = [
    ("☕ Kafe", "cafe"),
    ("📚 Kutubxona", "library"),
    ("💼 Kovorking", "coworking"),
    ("🆓 Bepul zona", "free_zone"),
    ("🎲 Hammasi", "all"),
]


def category_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=f"fcat:{code}")]
            for t, code in CATEGORY_OPTIONS
        ]
    )


NOISE_OPTIONS = [
    ("🤫 Juda tinch", "very_quiet"),
    ("😌 Tinch", "quiet"),
    ("🎵 O'rtacha", "moderate"),
    ("📢 Farqi yo'q", "all"),
]


def noise_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=f"fnoise:{code}")]
            for t, code in NOISE_OPTIONS
        ]
    )


OUTLET_OPTIONS = [
    ("🔌 Har stolda", "every_table"),
    ("⚡ Kamroq", "few"),
    ("❌ Kerak emas", "all"),
]


def outlets_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=f"fout:{code}")]
            for t, code in OUTLET_OPTIONS
        ]
    )


PRICE_OPTIONS = [
    ("🆓 Bepul", "free"),
    ("$ — arzon", "$"),
    ("$$ — o'rtacha", "$$"),
    ("💎 Narxi muhim emas", "all"),
]


def price_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=f"fprice:{code}")]
            for t, code in PRICE_OPTIONS
        ]
    )


def place_card_keyboard(place_id: int, is_favorite: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✅ Men hozir shu yerdaman", callback_data=f"occ:{place_id}:empty"),
            InlineKeyboardButton(text="📝 Sharh", callback_data=f"rev:{place_id}"),
        ],
        [
            InlineKeyboardButton(
                text="⭐ Sevimlilarga" if not is_favorite else "⭐ Sevimlilardan olish",
                callback_data=f"fav:{place_id}:{'add' if not is_favorite else 'remove'}",
            ),
            InlineKeyboardButton(text="ℹ️ Batafsil", callback_data=f"detail:{place_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def occupancy_keyboard(place_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🟢 Bo'sh", callback_data=f"occ:{place_id}:empty"),
                InlineKeyboardButton(text="🟡 O'rtacha", callback_data=f"occ:{place_id}:medium"),
                InlineKeyboardButton(text="🔴 To'la", callback_data=f"occ:{place_id}:full"),
            ]
        ]
    )


def review_rating_keyboard(place_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data=f"rate:{place_id}:1"),
                InlineKeyboardButton(text="2", callback_data=f"rate:{place_id}:2"),
                InlineKeyboardButton(text="3", callback_data=f"rate:{place_id}:3"),
                InlineKeyboardButton(text="4", callback_data=f"rate:{place_id}:4"),
                InlineKeyboardButton(text="5", callback_data=f"rate:{place_id}:5"),
            ]
        ]
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
        ]
    )
