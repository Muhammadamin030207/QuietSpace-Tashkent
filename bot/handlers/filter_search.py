from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import (
    cancel_keyboard,
    noise_keyboard,
    outlets_keyboard,
    place_card_keyboard,
    price_keyboard,
)
from services import context

from .main_menu import FilterStates

router = Router()


async def _cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Bekor qilindi. ❌")
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_cb(callback: CallbackQuery, state: FSMContext):
    await _cancel(callback, state)


@router.callback_query(FilterStates.category, F.data.startswith("fcat:"))
async def pick_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[1]
    if category == "all":
        category = None
    await state.update_data(category=category)
    await state.set_state(FilterStates.noise)
    await callback.message.edit_text("Shovqin darajasi:", reply_markup=noise_keyboard())
    await callback.answer()


@router.callback_query(FilterStates.noise, F.data.startswith("fnoise:"))
async def pick_noise(callback: CallbackQuery, state: FSMContext):
    noise = callback.data.split(":")[1]
    if noise == "all":
        noise = None
    await state.update_data(noise=noise)
    await state.set_state(FilterStates.outlets)
    await callback.message.edit_text("Rozetka darajasi:", reply_markup=outlets_keyboard())
    await callback.answer()


@router.callback_query(FilterStates.outlets, F.data.startswith("fout:"))
async def pick_outlets(callback: CallbackQuery, state: FSMContext):
    outlets = callback.data.split(":")[1]
    if outlets == "all":
        outlets = None
    await state.update_data(outlets=outlets)
    await state.set_state(FilterStates.price)
    await callback.message.edit_text("Narx darajasi:", reply_markup=price_keyboard())
    await callback.answer()


@router.callback_query(FilterStates.price, F.data.startswith("fprice:"))
async def pick_price(callback: CallbackQuery, state: FSMContext):
    price = callback.data.split(":")[1]
    if price == "all":
        price = None
    data = await state.get_data()
    await state.clear()

    filters = {}
    if data.get("category"):
        filters["category"] = data["category"]
    if data.get("noise"):
        filters["noise"] = data["noise"]
    if data.get("outlets"):
        filters["outlets"] = data["outlets"]
    if price:
        filters["price"] = price

    session = await context.get_session(callback)
    if session is None:
        await callback.message.answer("⚠️ Avval /start orqali kiring.")
        return
    try:
        places = await session.client.search(filters)
    except Exception:  # noqa: BLE001
        await callback.message.answer("⚠️ Qidiruvda xatolik.")
        return

    if not places:
        await callback.message.edit_text("😔 Bu filtrlarga mos joy topilmadi.")
        return

    await callback.message.edit_text(
        f"🎛 Filtr bo'yicha <b>{len(places)}</b> ta joy topildi:"
    )
    from services.format import place_card_text

    for place in places[:8]:
        await callback.message.answer(
            place_card_text(place),
            reply_markup=place_card_keyboard(place.get("id")),
        )
    await callback.answer()


@router.message((F.text == "Bekor") | (F.text == "❌ Bekor qilish"))
async def cancel_text(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi. ❌")
