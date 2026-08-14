from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline import (
    category_keyboard,
    mini_app_keyboard,
    noise_keyboard,
    outlets_keyboard,
    price_keyboard,
)
from services import context

router = Router()


@router.message(F.text == "🎛 Filtr bilan qidirish")
async def filter_search_start(message: Message, state: FSMContext):
    await state.set_state(FilterStates.category)
    await message.answer("Toifani tanlang:", reply_markup=category_keyboard())


@router.message(F.text == "🤖 AI bilan so'rash")
async def ai_dialog_start(message: Message, state: FSMContext):
    await state.set_state(FilterStates.ai_dialog)
    await message.answer(
        "🤖 AI yordamchi bilan gaplashing! Masalan:\n"
        "«Chilonzorda rozetkasi bor, jim kafe top»\n"
        "Yoki istalgan savolni bering. «Bekor» deb yozsangiz chiqasiz."
    )


@router.message(F.text == "⭐ Sevimlilar")
async def favorites_list(message: Message, state: FSMContext):
    session = await context.get_session(message)
    if session is None:
        await message.answer("⚠️ Avval /start orqali kirishingiz kerak.")
        return
    try:
        favorites = await session.client.my_favorites()
    except Exception:  # noqa: BLE001
        await message.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko'ring.")
        return
    if not favorites:
        await message.answer("⭐ Sevimlilar hozircha bo'sh.")
        return
    from keyboards.inline import place_card_keyboard
    from services.format import place_card_text

    for fav in favorites[:10]:
        place = fav.get("place", {})
        await message.answer(
            place_card_text(place),
            reply_markup=place_card_keyboard(place.get("id"), is_favorite=True),
        )


@router.message(F.text == "🌐 Mini App ochish")
async def open_mini_app(message: Message, state: FSMContext):
    await message.answer(
        "🌐 Telegram Mini App ochilmoqda — to'liq xarita, filtrlash va AI chat:",
        reply_markup=mini_app_keyboard(),
    )


@router.message((F.text == "📍 Joylashuv orqali qidirish") | F.location)
async def location_search(message: Message, state: FSMContext):
    if not message.location:
        await message.answer("📍 Joylashuvingizni yuboring (pastdagi tugma orqali):")
        return
    session = await context.get_session(message)
    if session is None:
        await message.answer("⚠️ Avval /start orqali kirishingiz kerak.")
        return
    lat = message.location.latitude
    lng = message.location.longitude
    await state.update_data(user_lat=lat, user_lng=lng)
    try:
        places = await session.client.nearby(lat, lng)
    except Exception:  # noqa: BLE001
        await message.answer("⚠️ Joylarni yuklashda xatolik.")
        return
    if not places:
        await message.answer("😔 Yaqin atrofda joy topilmadi.")
        return

    from keyboards.inline import place_card_keyboard
    from services.format import place_card_text

    await message.answer(f"📍 Yaqin atrofda <b>{len(places)}</b> ta joy topildi:")
    for place in places[:8]:
        await message.answer(
            place_card_text(place),
            reply_markup=place_card_keyboard(place.get("id")),
        )


from aiogram.fsm.state import State, StatesGroup


class FilterStates(StatesGroup):
    category = State()
    noise = State()
    outlets = State()
    price = State()
    ai_dialog = State()
    review_text = State()
    review_rating = State()
