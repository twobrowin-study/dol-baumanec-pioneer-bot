from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler
from telegram.ext import ChatMemberHandler, CallbackQueryHandler

from settings import BotToken
from log import Log

from handlers import ChatJoinHandler
from handlers import HelpHandler
from handlers import StartHandler
from handlers import StartRegisteredHandler
from handlers import NameHandler
from handlers import BirthHandler
from handlers import GroupHandler
from handlers import PhoneHandler
from handlers import ExpectionsHandler
from handlers import GetInfoHandler
from handlers import UnregisterHandler
from handlers import ReregisterHandler
from handlers import RegisterHandler
from handlers import Song1Handler
from handlers import Song2Handler
from handlers import Song3Handler
from handlers import RegisterCallbackHandler
from handlers import AfterRegisterCallbackHandler
from handlers import NotificationsCallbackHandler
from handlers import PhotoHandler

from filters import PrivateChatFilter
from filters import UserNotRegisteredFilter
from filters import UserIsRegisteredFilter
from filters import UserShouldWriteNameFilter
from filters import UserShouldWriteBirthFilter
from filters import UserShouldWriteGroupFilter
from filters import UserShouldWritePhoneFilter
from filters import UserShouldWriteExpectionsFilter
from filters import UserHasCallbackStatusFilter
from filters import UserShouldWriteSong1Filter
from filters import UserShouldWriteSong2Filter
from filters import UserShouldWriteSong3Filter
from filters import HasPhotoFilter

from commands import Commands
from answers import Answers
from groups import Groups
from expections import Expections
from notifications import Notifications

from commands import COMMAND_START
from commands import COMMAND_HELP
from commands import COMMAND_GETINFO
from commands import COMMAND_UNREGISTER
from commands import COMMAND_REREGISTER
from commands import COMMAND_REGISTER

async def post_init(application: Application) -> None:
    await app.bot.set_my_commands(Commands.get_commands_descriptions())
    application.create_task(Commands.update(application))
    application.create_task(Answers.update(application))
    application.create_task(Groups.update(application))
    application.create_task(Expections.update(application))
    application.create_task(Notifications.update(application))
    application.create_task(Notifications.send_notifications(application))

if __name__ == '__main__':
    Log.info("Starting...")
    app = ApplicationBuilder().token(BotToken).post_init(post_init).build()

    app.add_handler(ChatMemberHandler(ChatJoinHandler))

    app.add_handler(CommandHandler(COMMAND_START, StartHandler, filters=PrivateChatFilter & UserNotRegisteredFilter))
    app.add_handler(CommandHandler(COMMAND_START, StartRegisteredHandler, filters=PrivateChatFilter & UserIsRegisteredFilter))
    
    app.add_handler(CommandHandler(COMMAND_HELP, HelpHandler, filters = UserIsRegisteredFilter))
    app.add_handler(CommandHandler(COMMAND_GETINFO, GetInfoHandler, filters = UserIsRegisteredFilter))
    app.add_handler(CommandHandler(COMMAND_UNREGISTER, UnregisterHandler, filters = UserIsRegisteredFilter))
    app.add_handler(CommandHandler(COMMAND_REREGISTER, ReregisterHandler, filters = UserIsRegisteredFilter))
    app.add_handler(CommandHandler(COMMAND_REGISTER, RegisterHandler, filters = UserIsRegisteredFilter))

    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserShouldWriteNameFilter, NameHandler))
    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserShouldWriteBirthFilter, BirthHandler))
    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserShouldWriteGroupFilter, GroupHandler))
    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserShouldWritePhoneFilter, PhoneHandler))
    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserShouldWriteExpectionsFilter, ExpectionsHandler))

    app.add_handler(CallbackQueryHandler(RegisterCallbackHandler, pattern='register_[a-z]+'))
    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserHasCallbackStatusFilter, AfterRegisterCallbackHandler))

    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserShouldWriteSong1Filter, Song1Handler))
    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserShouldWriteSong2Filter, Song2Handler))
    app.add_handler(MessageHandler(UserIsRegisteredFilter & UserShouldWriteSong3Filter, Song3Handler))

    app.add_handler(CallbackQueryHandler(NotificationsCallbackHandler, pattern='notifications_[a-z]+'))

    app.add_handler(MessageHandler(PrivateChatFilter & HasPhotoFilter, PhotoHandler))

    app.run_polling()
    Log.info("Done. Goodby!")