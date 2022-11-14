import pandas as pd

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application
from telegram.constants import ParseMode

from sheet import AbstractSheetAdapter

from settings import SheetAnswers
from log import Log

from groups import Groups

from datetime import datetime

NAME_QUESTION = 'Фамилия Имя Отчество *(это БАЗА)*'
BIRTH_QUESTION = 'Дата рождения _(пример: 01.01.2001)_'
GROUP_QUESTION = 'Учебная группа _(пример: МТ2-11Б)_'
PHONE_QUESTION = 'Номер телефона _(пример: +79017495904)_'
EXPECTIONS_QUESTION = 'Что ожидаешь от выезда???'
SONG_QUESTION_1 = 'Напиши три песни, которые тебе хотелось бы услышать на дискотеке _(тремя сообщениями, а не хочешь - не пиши)_'
SONG_QUESTION_2 = 'И вторую'
SONG_QUESTION_3 = 'И третью'

ACTIVE = 'Запись активна? (Пользователь может убрать подтверждение заранее)'
CONFIRM = 'Подтверждающая отметочка (какого-то числа отправим сообщение)'
FEEDBACK = 'ОтветОЧКА'

NAME_CALLBACK   = 'register_name'
BIRTH_CALLBACK  = 'register_birth'
GROUP_CALLBACK  = 'register_group'
PHONE_CALLBACK  = 'register_phone'
SONG_CALLBACK_1 = 'register_song_1'
SONG_CALLBACK_2 = 'register_song_2'
SONG_CALLBACK_3 = 'register_song_3'
FEEDBACK_CALLBACK = 'register_feedback'

class AnswersClass(AbstractSheetAdapter):
    def __init__(self, sheet_name: str, name: str) -> None:
        super().__init__(sheet_name, name)
        self.status = pd.DataFrame()

    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
        if full_df.empty:
            return full_df
        valid = full_df.loc[
            (full_df['Отметка времени'] != '') |
            (full_df[NAME_QUESTION] != '') |
            (full_df[BIRTH_QUESTION] != '') |
            (full_df[GROUP_QUESTION] != '') |
            (full_df[PHONE_QUESTION] != '') |
            (full_df['Скинь ссылочку на тг))'] != '') |
            (full_df[EXPECTIONS_QUESTION] != '') |
            (full_df['Id Telegram'] != '') |
            (full_df[ACTIVE] != '') |
            (full_df[CONFIRM] != '') |
            (full_df[SONG_QUESTION_1] != '') |
            (full_df[SONG_QUESTION_2] != '') |
            (full_df[SONG_QUESTION_3] != '') |
            (full_df[FEEDBACK] != '')
        ]
        return valid
    
    def _write_data_by_collumn_name(self, row: int, col_name: str, val: str|int) -> None:
        col  = self.wks.find(col_name).col
        self.wks.update_cell(row, col, val)
    
    def _find_row_by_chat_id(self, chat_id: int) -> int:
        return self.wks.find(str(chat_id)).row
    
    def get_all_fully_registered_active_user_ids(self) -> list[int]:
        if self.valid.empty:
            return []
        return self.valid.loc[
            (self.valid['Отметка времени'] != '') &
            (self.valid[NAME_QUESTION] != '') &
            (self.valid[BIRTH_QUESTION] != '') &
            (self.valid[GROUP_QUESTION] != '') &
            (self.valid[PHONE_QUESTION] != '') &
            (self.valid['Скинь ссылочку на тг))'] != '') &
            (self.valid[EXPECTIONS_QUESTION] != '') &
            (self.valid['Id Telegram'] != '') &
            (self.valid[ACTIVE] == 'Да')
        ]['Id Telegram'].to_list()
    
    def check_user_not_registered(self, chat_id: int) -> bool:
        if self.valid.empty:
            return True
        return self.valid.loc[self.valid['Id Telegram'] == chat_id].empty

    def check_user_is_registered(self, chat_id: int) -> bool:
        return not self.check_user_not_registered(chat_id)
    
    def check_user_should_write_question(self, chat_id: int, question: str) -> bool:
        tmp_df = self.valid.loc[
            (self.valid['Id Telegram'] == chat_id) &
            (
                (self.valid[question] == "") | 
                (self.valid[question] == None)
            )
        ]
        return not tmp_df.empty
    
    def start_registration(self, chat_id: int, username: str, app: Application) -> None:
        if self.check_user_is_registered(chat_id):
            return
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tmp_df = pd.DataFrame({
            'Отметка времени': date,
            NAME_QUESTION: "",
            BIRTH_QUESTION: "",
            GROUP_QUESTION: "",
            PHONE_QUESTION: "",
            'Скинь ссылочку на тг))': username,
            EXPECTIONS_QUESTION: "",
            'Id Telegram': chat_id,
            ACTIVE: "",
            CONFIRM: "",
            SONG_QUESTION_1: "",
            SONG_QUESTION_2: "",
            SONG_QUESTION_3: "",
            FEEDBACK: ""
        }, index=[0])
        if self.valid.empty:
            self.valid = tmp_df
        else:
            self.valid = pd.concat([self.valid, tmp_df], ignore_index=True)
        Log.info(f"Wrote to {self.name} df from registration")
        Log.debug(self.valid)
        app.create_task(self._start_registration_wks(date, chat_id, username))

    async def _start_registration_wks(self, date: str, chat_id: int, username: str) -> None:
        Log.debug("_start_registration_wks started")
        row = self._next_available_row()
        self._write_data_by_collumn_name(row, 'Отметка времени', date)
        self._write_data_by_collumn_name(row, 'Id Telegram', chat_id)
        self._write_data_by_collumn_name(row, 'Скинь ссылочку на тг))', username)
        Log.debug("_start_registration_wks complete")
    
    def write_answer(self, question: str, chat_id: int, value: str, app: Application) -> None:
        self.valid.loc[self.valid['Id Telegram'] == chat_id, question] = value
        Log.info(f"Wrote to {self.name} df from {question}")
        Log.debug(self.valid)
        app.create_task(self._write_answer_wks(question, chat_id, value))

    async def _write_answer_wks(self, question: str, chat_id: int, value: str) -> None:
        Log.debug(f"_write_name_wks from {question} started")
        row = self._find_row_by_chat_id(chat_id)
        self._write_data_by_collumn_name(row, question, value)
        Log.debug(f"_write_name_wks from {question} complete")
    
    def registration_complete(self, chat_id: int, app: Application) -> None:
        self.write_answer(ACTIVE, chat_id, "Да", app)
        if self.valid.shape[0] == 1:
            self._send_to_all_groups("У нас *первый* зарегистрированный на выезд!", app)
        if self.valid.shape[0]%10 == 0:
            self._send_to_all_groups(f"У нас уже *{self.valid.shape[0]}* зарегистрированных на выезд!", app)
            
    def _send_to_all_groups(self, message: str, app: Application) -> None:
        for group_id in Groups.get_all_groups():
            app.create_task(app.bot.send_message(group_id, message, parse_mode = ParseMode.MARKDOWN))
    
    def get_user_info_markup_by_id(self, chat_id: int) -> InlineKeyboardMarkup:
        for _,row in self.valid.loc[self.valid['Id Telegram'] == chat_id].iterrows():
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(text=row[NAME_QUESTION], callback_data = NAME_CALLBACK)],
                [InlineKeyboardButton(text=row[BIRTH_QUESTION], callback_data = BIRTH_CALLBACK)],
                [InlineKeyboardButton(text=row[GROUP_QUESTION], callback_data = GROUP_CALLBACK)],
                [InlineKeyboardButton(text=row[PHONE_QUESTION], callback_data = PHONE_CALLBACK)],
                [
                    InlineKeyboardButton(text=row[SONG_QUESTION_1], callback_data = SONG_CALLBACK_1),
                    InlineKeyboardButton(text=row[SONG_QUESTION_2], callback_data = SONG_CALLBACK_2),
                    InlineKeyboardButton(text=row[SONG_QUESTION_3], callback_data = SONG_CALLBACK_3)
                ],
            ])
        return InlineKeyboardMarkup()
    
    def set_user_status_message_id(self, chat_id: int, message_id: int) -> None:
        tmp_df = pd.DataFrame({
            "chat_id": chat_id,
            "callback_data": '',
            "message_id": message_id
        }, index=[0])
        if self.status.empty:
            self.status = tmp_df
        elif not self.status.loc[self.status.chat_id == chat_id]:
            self.status.loc[self.status.chat_id == chat_id, 'message_id'] = message_id
        else:
            self.status = pd.concat([self.status, tmp_df], ignore_index=True)
        Log.info(f"Wrote to {self.name} status df:")
        Log.debug(self.status)
    
    def set_user_status_after_callback(self, chat_id: int, callback_data: str) -> None:
        tmp_df = pd.DataFrame({
            "chat_id": chat_id,
            "callback_data": callback_data,
            "message_id": None
        }, index=[0])
        if self.status.empty:
            self.status = tmp_df
        elif not self.status.loc[self.status.chat_id == chat_id].empty:
            self.status.loc[self.status.chat_id == chat_id, 'callback_data'] = callback_data
        else:
            self.status = pd.concat([self.status, tmp_df], ignore_index=True)
        Log.info(f"Wrote to {self.name} status df:")
        Log.debug(self.status)
    
    def check_if_user_status_is_set(self, chat_id: int):
        if self.status.empty:
            return False
        return not self.status.loc[
            (self.status.chat_id == chat_id) &
            (self.status.callback_data != "")
        ].empty
    
    def update_user_by_status(self, chat_id: int, value: str, app: Application) -> int:
        for _,row in self.status.loc[self.status.chat_id == chat_id].iterrows():
            if row.callback_data == NAME_CALLBACK:
                self.write_answer(NAME_QUESTION, chat_id, value, app)
            if row.callback_data == BIRTH_CALLBACK:
                self.write_answer(BIRTH_QUESTION, chat_id, value, app)
            if row.callback_data == GROUP_CALLBACK:
                self.write_answer(GROUP_QUESTION, chat_id, value, app)
            if row.callback_data == PHONE_CALLBACK:
                self.write_answer(PHONE_QUESTION, chat_id, value, app)
            if row.callback_data == SONG_CALLBACK_1:
                self.write_answer(SONG_QUESTION_1, chat_id, value, app)
            if row.callback_data == SONG_CALLBACK_2:
                self.write_answer(SONG_QUESTION_2, chat_id, value, app)
            if row.callback_data == SONG_CALLBACK_3:
                self.write_answer(SONG_QUESTION_3, chat_id, value, app)
            if row.callback_data == FEEDBACK_CALLBACK:
                self.write_answer(FEEDBACK, chat_id, value, app)
            message_id = row.message_id
        self.status = self.status.drop(self.status[self.status.chat_id == chat_id].index)
        Log.info(f"Deleted from {self.name} status df:")
        Log.debug(self.status)
        return message_id

Answers = AnswersClass(SheetAnswers, 'answers')