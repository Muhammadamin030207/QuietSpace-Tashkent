from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline import place_card_keyboard
from services import context

from .main_menu import FilterStates

router = Router()


@router.message(FilterStates.ai_dialog)
async def ai_dialog_message(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.lower() in ("bekor", "cancel", "exit"):
        await state.clear()
        await message.answer("AI dialog yakunlandi. 👋")
        return

    session = await context.get_session(message)
    if session is None:
        await message.answer("⚠️ Avval /start orqali kiring.")
        return

    data = await state.get_data()
    user_lat = data.get("user_lat")
    user_lng = data.get("user_lng")

    await message.answer("🤖 AI izlayapti... bir soniya")
    try:
        result = await session.client.ai_chat(text, user_lat, user_lng, channel="bot")
    except Exception:  # noqa: BLE001
        await message.answer("⚠️ AI xizmati hozircha ishlamayapti. Keyinroq urinib ko'ring.")
        return

    reply = result.get("reply") or "Nimadir noto'g'ri ketdi."
    await message.answer(reply, parse_mode="HTML")

    places = result.get("places", [])
    for place in places[:8]:
        from services.format import place_card_text

        # build display dict for formatter
        display = {
            "name": place["name"],
            "category": {"key": place.get("category"), "name_uz": place.get("category", "")},
            "district": place.get("district", ""),
            "address": place.get("address", ""),
            "avg_rating": place.get("rating", 0),
            "distance_km": None,
            "occupancy": None,
            "wifi_speed": place.get("wifi", ""),
            "noise_level": place.get("noise", ""),
            "outlets_level": place.get("outlets", ""),
            "price_level": place.get("price", ""),
        }
        await message.answer(
            place_card_text(display),
            reply_markup=place_card_keyboard(
                place.get("id"), is_favorite=place.get("is_favorite", False)
            ),
        )


@router.message()
async def unknown_text(message: Message, state: FSMContext):
    from keyboards.inline import main_menu_keyboard

    await message.answer(
        "Quyidagi menyudan foydalaning 👇", reply_markup=main_menu_keyboard()
    )
