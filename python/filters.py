from telegram import Message
from telegram.ext.filters import MessageFilter

from answers import Answers

from answers import NAME_QUESTION
from answers import BIRTH_QUESTION
from answers import GROUP_QUESTION
from answers import PHONE_QUESTION
from answers import EXPECTIONS_QUESTION

class PrivateChatClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.chat.type == 'private'
PrivateChatFilter = PrivateChatClass()

class UserNotRegisteredClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Answers.check_user_not_registered(message.chat_id)
UserNotRegisteredFilter = UserNotRegisteredClass()

class UserIsRegisteredClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Answers.check_user_is_registered(message.chat_id)
UserIsRegisteredFilter = UserIsRegisteredClass()

class UserShouldWriteNameClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Answers.check_user_should_write_question(message.chat_id, NAME_QUESTION)
UserShouldWriteNameFilter = UserShouldWriteNameClass()

class UserShouldWriteBirthClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Answers.check_user_should_write_question(message.chat_id, BIRTH_QUESTION)
UserShouldWriteBirthFilter = UserShouldWriteBirthClass()

class UserShouldWriteGroupClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Answers.check_user_should_write_question(message.chat_id, GROUP_QUESTION)
UserShouldWriteGroupFilter = UserShouldWriteGroupClass()

class UserShouldWritePhoneClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Answers.check_user_should_write_question(message.chat_id, PHONE_QUESTION)
UserShouldWritePhoneFilter = UserShouldWritePhoneClass()

class UserShouldWriteExpectionsClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Answers.check_user_should_write_question(message.chat_id, EXPECTIONS_QUESTION)
UserShouldWriteExpectionsFilter = UserShouldWriteExpectionsClass()

class UserHasCallbackStatusClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Answers.check_if_user_status_is_set(message.chat_id)
UserHasCallbackStatusFilter = UserHasCallbackStatusClass()