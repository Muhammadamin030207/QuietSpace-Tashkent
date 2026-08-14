from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import (
    cancel_keyboard,
    occupancy_keyboard,
    place_card_keyboard,
    review_rating_keyboard,
)
from services import context

from .main_menu import FilterStates

router = Router()


@router.callback_query(F.data.startswith("detail:"))
async def place_detail(callback: CallbackQuery, state: FSMContext):
    place_id = int(callback.data.split(":")[1])
    session = await context.get_session(callback)
    if session is None:
        await callback.answer("⚠️ Avval /start orqali kiring.")
        return
    try:
        place = await session.client.place_detail(place_id)
    except Exception:  # noqa: BLE001
        await callback.answer("⚠️ Xatolik yuz berdi.")
        return

    from services.format import place_card_text

    lines = [place_card_text(place)]
    if place.get("description"):
        lines.append(f"\n📝 {place['description']}")
    try:
        summary = await session.client.ai_summary(place_id)
        if summary.get("summary"):
            lines.append(f"\n✨ <i>AI xulosa: {summary['summary']}</i>")
    except Exception:  # noqa: BLE001
        pass

    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("occ:"))
async def report_occupancy(callback: CallbackQuery, state: FSMContext):
    _, place_id, level = callback.data.split(":")
    session = await context.get_session(callback)
    if session is None:
        await callback.answer("⚠️ Avval /start orqali kiring.")
        return
    ok = await session.client.report_occupancy(int(place_id), level)
    labels = {"empty": "🟢 Bo'sh", "medium": "🟡 O'rtacha", "full": "🔴 To'la"}
    if ok:
        await callback.answer(f"✅ Hisobot qabul qilindi: {labels.get(level, level)}")
        await callback.message.answer(
            f"✅ <b>{labels.get(level, level)}</b> deb belgilandingiz. Rahmat!",
            parse_mode="HTML",
        )
    else:
        await callback.answer("⚠️ Xatolik. Qayta urinib ko'ring.")


@router.callback_query(F.data.startswith("fav:"))
async def toggle_favorite(callback: CallbackQuery, state: FSMContext):
    _, place_id, action = callback.data.split(":")
    session = await context.get_session(callback)
    if session is None:
        await callback.answer("⚠️ Avval /start orqali kiring.")
        return
    try:
        if action == "add":
            ok = await session.client.add_favorite(int(place_id))
            text = "⭐ Sevimlilarga qo'shildi!"
        else:
            ok = await session.client.remove_favorite(int(place_id))
            text = "Sevimlilardan olib tashlandi."
        await callback.answer(text if ok else "⚠️ Xatolik")
        if ok:
            await callback.message.answer(text)
    except Exception:  # noqa: BLE001
        await callback.answer("⚠️ Xatolik yuz berdi.")


@router.callback_query(F.data.startswith("rev:"))
async def start_review(callback: CallbackQuery, state: FSMContext):
    place_id = int(callback.data.split(":")[1])
    await state.set_state(FilterStates.review_text)
    await state.update_data(review_place_id=place_id)
    await callback.message.answer(
        "📝 Sharh matnini yozing (yoki «Bekor»):",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(FilterStates.review_text)
async def review_text_received(message: Message, state: FSMContext):
    if (message.text or "").lower() in ("bekor", "cancel"):
        await state.clear()
        await message.answer("Bekor qilindi. ❌")
        return
    data = await state.get_data()
    place_id = data.get("review_place_id")
    await state.set_state(FilterStates.review_rating)
    await state.update_data(review_text=message.text or "")
    await message.answer(
        "Reyting bering (1-5):", reply_markup=review_rating_keyboard(place_id)
    )


@router.callback_query(FilterStates.review_rating, F.data.startswith("rate:"))
async def review_submit(callback: CallbackQuery, state: FSMContext):
    _, place_id, rating = callback.data.split(":")
    data = await state.get_data()
    await state.clear()
    session = await context.get_session(callback)
    if session is None:
        await callback.answer("⚠️ Avval /start orqali kiring.")
        return
    try:
        review = await session.client.add_review(
            int(place_id), int(rating), data.get("review_text", "")
        )
        await callback.answer("✅ Sharh qoldirildi!")
        await callback.message.answer(
            "✅ Sharhingiz qabul qilindi! Reyting: {}/5. AI tekshiruvidan o'tmoqda.".format(rating)
        )
    except Exception:  # noqa: BLE001
        await callback.answer("⚠️ Sharh yuborishda xatolik.")


@router.callback_query(F.data.startswith("occx:"))
async def show_occupancy_options(callback: CallbackQuery, state: FSMContext):
    place_id = int(callback.data.split(":")[1])
    await callback.message.answer(
        "Hozirgi bandlik holatini tanlang:",
        reply_markup=occupancy_keyboard(place_id),
    )
    await callback.answer()
