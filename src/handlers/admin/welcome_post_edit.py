import json

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

from src.misc.admin_states import EditWelcomeStates
from config import Config


class Keyboards:
    reply_button_for_admin_menu = KeyboardButton('✏ Изменить приветствие ✏')

    @staticmethod
    def get_cancel_or_save_welcome_changes() -> InlineKeyboardMarkup:
        commit_button = InlineKeyboardButton(text='💾 Сохранить', callback_data='save_welcome_post_changes')
        cancel_button = InlineKeyboardButton(text='🔙 Отмена', callback_data='cancel_welcome_post_editing')
        return InlineKeyboardMarkup().add(commit_button).row(cancel_button)


class Handlers:
    @classmethod
    async def __handle_admin_edit_content_button(cls, message: Message, state: FSMContext):
        await message.answer(
            text='Отправьте сообщение с новым приветствием:',
            reply_markup=Keyboards.get_cancel_or_save_welcome_changes()
        )
        await state.set_state(EditWelcomeStates.wait_for_new_content)

    @classmethod
    async def __handle_new_welcome_text(cls, message: Message, state: FSMContext):
        await state.update_data(text=message.html_text)

    @classmethod
    async def __handle_new_welcome_images(cls, message: Message, state: FSMContext):
        data = await state.get_data()
        images_file_id = message.photo[0].file_id

        current_images = data.get('images') if bool(data.get('images')) else []
        current_images.append(images_file_id)
        await state.update_data(images=current_images)

    @classmethod
    async def __handle_save_changes_callback(cls, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.answer('Изменения сохранены ✅')
        new_data = await state.get_data()

        with open(Config.Paths.WELCOME_POST_CONTENT_JSON, 'r') as welcome_content:
            current_data = json.loads(welcome_content.read())

        if new_data.get('text'):
            current_data['text'] = new_data['text']
        current_data['images'] = new_data['images'] if new_data.get('images') else []

        with open(Config.Paths.WELCOME_POST_CONTENT_JSON, 'w') as welcome_content:
            json.dump(current_data, welcome_content, indent=4)

        await state.finish()

    @classmethod
    async def __handle_cancel_welcome_content_edit(cls, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await state.finish()
        await callback.message.answer('Изменение приветствия отменено ❌')

    @classmethod
    def register_admin_welcome_post_edit_handlers(cls, dp: Dispatcher):
        dp.register_message_handler(
            cls.__handle_admin_edit_content_button, is_admin=True,
            text=Keyboards.reply_button_for_admin_menu.text
        )

        dp.register_message_handler(
            cls.__handle_new_welcome_text,
            state=EditWelcomeStates.wait_for_new_content,
            content_types=['text']
        )
        dp.register_message_handler(
            cls.__handle_new_welcome_images,
            state=EditWelcomeStates.wait_for_new_content,
            content_types=['photo']
        )

        dp.register_callback_query_handler(
            cls.__handle_save_changes_callback,
            text='save_welcome_post_changes',
            state=EditWelcomeStates.wait_for_new_content
        )

        dp.register_callback_query_handler(
            cls.__handle_cancel_welcome_content_edit,
            text='cancel_welcome_post_editing',
            state=EditWelcomeStates.wait_for_new_content
        )

