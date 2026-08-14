from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import language_keyboard, mini_app_keyboard
from services import context
from services.format import place_card_text

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Bu — <b>QuietSpace Tashkent</b> boti. Toshkentdagi tinch, ishlashga qulay "
        "joylarni topishda yordam beraman: kafelar, kutubxonalar, kovorkinglar va bepul zonalar.\n\n"
        "Iltimos, tilni tanlang:",
        reply_markup=language_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await state.update_data(language=lang)
    session = await context.get_session(callback)
    if session is None:
        await callback.message.answer("⚠️ Login xatosi. Qayta /start qiling.")
        return
    try:
        await session.client.request(
            "PATCH", "api/auth/me/", json={"language": lang}
        )
    except Exception:  # noqa: BLE001
        pass

    texts = {
        "uz": "Tayyor! 🎉 Quyidagi menyudan foydalaning:",
        "ru": "Готово! 🎉 Используйте меню ниже:",
        "en": "Done! 🎉 Use the menu below:",
    }
    await callback.message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=context_main_menu(lang),
    )
    await callback.message.answer(
        "🌐 Mini App orqali to'liq xarita va filtrlardan foydalanishingiz mumkin:",
        reply_markup=mini_app_keyboard(),
    )
    await callback.answer()


def context_main_menu(lang: str):
    from keyboards.inline import main_menu_keyboard

    return main_menu_keyboard()
