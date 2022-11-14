import asyncio
import pandas as pd

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application
from telegram.constants import ParseMode

from sheet import AbstractSheetAdapter

from settings import SheetNotifications, NotificationsTimeout
from log import Log

from answers import Answers
from groups import Groups

from answers import FEEDBACK_CALLBACK 

from datetime import datetime

from telegram import PhotoSize
import json

YES_TEXT = 'Да'
NO_TEXT = 'Нет'
YES_CALLBACK = 'notifications_yes'
NO_CALLBACK = 'notifications_no'

class NotificationsClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
        if full_df.empty:
            return full_df
        valid = full_df.loc[
            (full_df['Сообщения, которые надо разослать'] != '') &
            (full_df['Дата и время'] != '') &
            (full_df['Сбор данных в колонку подтверждения?'] != '') &
            (full_df['Активно?'] != '') &
            (full_df['Отправлено?'] != '') &
            (full_df['ОтветОЧКА?'] != '') &
            (full_df['Фото'] != '')
        ]
        return valid
    
    def _get_notifications_to_send(self) -> pd.DataFrame:
        try:
            self.valid['Дата и время'] = self.valid['Дата и время'].apply(lambda s: datetime.strptime(str(s), "%d.%m.%Y %H:%M:%S"))
        except Exception:
            self.valid['Дата и время'] = self.valid['Дата и время'].apply(lambda s: datetime.strptime(str(s), "%Y-%m-%d %H:%M:%S"))
        return self.valid.loc[
            (self.valid['Дата и время'] <= datetime.now()) &
            (self.valid['Активно?'] == 'Да') &
            (self.valid['Отправлено?'] == 'Нет')
        ]
    
    async def send_notifications(self, app: Application):
        await asyncio.sleep(NotificationsTimeout)
        app.create_task(self.send_notifications(app))
        Log.info("Check for nottifications")
        for _,row in self._get_notifications_to_send().iterrows():
            Log.info("Send notification")
            Log.debug(row)
            message = row['Сообщения, которые надо разослать']

            has_photo = False
            if row['Фото'] != '' and row['Фото'] != None:
                has_photo = True
                json_tmp = json.loads(row['Фото'])
                photo_obj = PhotoSize.de_json(json_tmp, app.bot)

            for chat_id in Answers.get_all_fully_registered_active_user_ids():
                try:
                    if has_photo == False:
                        await app.bot.send_message(chat_id, message, parse_mode = ParseMode.MARKDOWN, disable_web_page_preview=True,
                            reply_markup = InlineKeyboardMarkup([
                                [InlineKeyboardButton(text=YES_TEXT, callback_data = YES_CALLBACK)],
                                [InlineKeyboardButton(text=NO_TEXT, callback_data = NO_CALLBACK)],
                            ]) if row['Сбор данных в колонку подтверждения?'] == 'Да' else None
                        )
                    else:
                        await app.bot.send_photo(chat_id, photo_obj, caption = message, parse_mode = ParseMode.MARKDOWN,
                            reply_markup = InlineKeyboardMarkup([
                                [InlineKeyboardButton(text=YES_TEXT, callback_data = YES_CALLBACK)],
                                [InlineKeyboardButton(text=NO_TEXT, callback_data = NO_CALLBACK)],
                            ]) if row['Сбор данных в колонку подтверждения?'] == 'Да' else None
                        )
                    if row['ОтветОЧКА?'] == 'Да':
                        Answers.set_user_status_after_callback(chat_id, FEEDBACK_CALLBACK)
                except Exception as e:
                    Log.debug("Got an exception")
            group_message = "Следующее сообщение было разослано только что всем участникам"
            for group_id in Groups.get_all_groups():
                await app.bot.send_message(group_id, group_message, parse_mode = ParseMode.MARKDOWN, disable_web_page_preview=True)
                if has_photo == False:
                    await app.bot.send_message(group_id, message, parse_mode = ParseMode.MARKDOWN, disable_web_page_preview=True)
                else:
                    await app.bot.send_photo(group_id, photo_obj, caption = message, parse_mode = ParseMode.MARKDOWN)
            
            self.valid.loc[self.valid['Сообщения, которые надо разослать'] == message, 'Отправлено?'] = 'Да'
            wks_row = self.wks.find(message).row
            wks_col = self.wks.find('Отправлено?').col
            self.wks.update_cell(wks_row, wks_col, 'Да')

Notifications = NotificationsClass(SheetNotifications, 'notifications')