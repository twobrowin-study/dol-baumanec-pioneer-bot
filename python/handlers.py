from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from commands import Commands
from answers import Answers
from expections import Expections

from commands import COMMAND_START
from commands import COMMAND_HELP
from commands import COMMAND_END
from commands import COMMAND_GETINFO
from commands import COMMAND_UNREGISTER
from commands import COMMAND_REREGISTER
from commands import COMMAND_REGISTER

from answers import NAME_QUESTION
from answers import BIRTH_QUESTION
from answers import GROUP_QUESTION
from answers import PHONE_QUESTION
from answers import EXPECTIONS_QUESTION
from answers import ACTIVE
from answers import CONFIRM

from notifications import YES_TEXT
from notifications import NO_TEXT
from notifications import YES_CALLBACK
from notifications import NO_CALLBACK

from log import Log

async def ChatJoinHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"I've join chat {update.effective_chat.id}")

async def HelpHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Commands.get_responce_to_command(COMMAND_HELP))

async def StartHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Commands.get_responce_to_command(COMMAND_START))
    await update.message.reply_markdown("Теперь ответь на несколько вопросов:")
    await update.message.reply_markdown(NAME_QUESTION)
    Answers.start_registration(update.effective_chat.id, update.effective_user.username, context.application)

async def StartRegisteredHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Commands.get_responce_to_registered_user(COMMAND_START))

async def NameHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(BIRTH_QUESTION)
    Answers.write_answer(NAME_QUESTION, update.effective_chat.id, update.message.text, context.application)

async def BirthHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(GROUP_QUESTION)
    Answers.write_answer(BIRTH_QUESTION, update.effective_chat.id, update.message.text, context.application)

async def GroupHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(PHONE_QUESTION)
    Answers.write_answer(GROUP_QUESTION, update.effective_chat.id, update.message.text, context.application)

async def PhoneHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(EXPECTIONS_QUESTION, reply_markup=Expections.get_keyboard_markup())
    Answers.write_answer(PHONE_QUESTION, update.effective_chat.id, update.message.text, context.application)

async def ExpectionsHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Commands.get_responce_to_command(COMMAND_END), reply_markup=ReplyKeyboardRemove())
    Answers.write_answer(EXPECTIONS_QUESTION, update.effective_chat.id, update.message.text, context.application)
    Answers.registration_complete(update.effective_chat.id, context.application)

async def GetInfoHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Commands.get_responce_to_command(COMMAND_GETINFO))

async def UnregisterHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Commands.get_responce_to_command(COMMAND_UNREGISTER))
    Answers.write_answer(ACTIVE, update.effective_chat.id, "Нет", context.application)

async def ReregisterHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Commands.get_responce_to_command(COMMAND_REREGISTER))
    Answers.write_answer(ACTIVE, update.effective_chat.id, "Да", context.application)

async def RegisterHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = await update.message.reply_markdown(
        Commands.get_responce_to_command(COMMAND_REGISTER),
        reply_markup=Answers.get_user_info_markup_by_id(update.effective_chat.id)
    )
    Answers.set_user_status_message_id(update.effective_chat.id, message.id)

async def RegisterCallbackHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await context.bot.send_message(update.effective_chat.id, "Введи новое значение:")
    Answers.set_user_status_after_callback(update.effective_chat.id, update.callback_query.data)

async def AfterRegisterCallbackHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_markdown("Записано")
    message_id = Answers.update_user_by_status(update.effective_chat.id, update.effective_message.text, context.application)
    try:
        await context.application.bot.edit_message_text(
            Commands.get_responce_to_command(COMMAND_REGISTER),
            chat_id=update.effective_chat.id,
            message_id=message_id,
            reply_markup=Answers.get_user_info_markup_by_id(update.effective_chat.id)
        )
    except Exception:
        Log.debug("Was not able to edit a message")

async def NotificationsCallbackHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    if update.callback_query.data == YES_CALLBACK:
        await context.bot.send_message(update.effective_chat.id, "Ты подтвердил своё участие. Молодцом!\n\nЕсли изменишь своё мнение, жмякай выше!")
        Answers.write_answer(CONFIRM, update.effective_chat.id, YES_TEXT, context.application)
        return
    if update.callback_query.data == NO_CALLBACK:
        await context.bot.send_message(update.effective_chat.id, "Очень жаль, что у тебя не получится...\n\nЕсли изменишь своё мнение, жмякай выше!")
        Answers.write_answer(CONFIRM, update.effective_chat.id, NO_TEXT, context.application)