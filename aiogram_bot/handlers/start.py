from aiogram import types, Router, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatMemberUpdated

from database.requests import create_user, get_user_subscription_status, change_user_subscription_status
from keyboards.inline_keyboards import subscription_keyboard, main_menu
from utils.check_subscription import check_subscription_telegram

start_command_router = Router()


@start_command_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext | None):
    if state is not None:
        if not await state.get_state() is None:
            data = await state.get_data()
            if 'sent_invoice' in data:
                sent_invoice = data['sent_invoice']
                await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_invoice)
            if 'message_id' in data:
                message_id = data['message_id']
                await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
            await state.update_data({})
            await state.clear()
    user = await create_user(user_id=message.chat.id, username=message.chat.username)
    if user is not None:
        if user.is_subscription_complete:
            await message.answer(text="Добро пожаловать!", reply_markup=await main_menu())
        else:
            await message.answer(text='Для того чтоб пользоваться ботом подпишитесь пожалуйста на наши каналы и чаты',
                                 reply_markup=await subscription_keyboard())
    else:
        await message.answer(text='error! Try again later please!')


@start_command_router.callback_query(F.data == 'main_menu')
async def main_menu_funciton(query: CallbackQuery, state: FSMContext | None):
    await query.answer()
    if state is not None:
        if not await state.get_state() is None:
            await state.update_data({})
            await state.clear()
    await query.message.edit_text(text="Главное меню:", reply_markup=await main_menu())


@start_command_router.callback_query(F.data == 'ignore')
async def ignore_function(query: CallbackQuery):
    await query.answer()


@start_command_router.callback_query(F.data == 'check_subscriptions')
async def checking_subscription(query: CallbackQuery):
    chats = await check_subscription_telegram(bot=query.message.bot, user_id=query.message.chat.id)
    if len(chats) == 0:
        await query.answer()
        await query.message.edit_text(text="Спасибо что подписались!✅\nДобро пожаловать!",
                                      reply_markup=await main_menu())
    else:
        await query.answer(text='❌Проверка не пройдена! Проверьте пожалуйста свои подписки!', show_alert=True)


@start_command_router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated):
    user_id = event.new_chat_member.user.id
    await change_user_subscription_status(user_id=user_id, status=False)
