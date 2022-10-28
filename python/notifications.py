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

from datetime import datetime

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
            (full_df['Отправлено?'] != '')
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
            for chat_id in Answers.get_all_fully_registered_active_user_ids():
                await app.bot.send_message(chat_id, message, parse_mode = ParseMode.MARKDOWN, disable_web_page_preview=True,
                    reply_markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton(text=YES_TEXT, callback_data = YES_CALLBACK)],
                        [InlineKeyboardButton(text=NO_TEXT, callback_data = NO_CALLBACK)],
                    ]) if row['Сбор данных в колонку подтверждения?'] == 'Да' else None
                )
            group_message = "Следующее сообщение было разослано только что всем участникам"
            for group_id in Groups.get_all_groups():
                await app.bot.send_message(group_id, group_message, parse_mode = ParseMode.MARKDOWN, disable_web_page_preview=True)
                await app.bot.send_message(group_id, message, parse_mode = ParseMode.MARKDOWN, disable_web_page_preview=True)
            
            self.valid.loc[self.valid['Сообщения, которые надо разослать'] == message, 'Отправлено?'] = 'Да'
            wks_row = self.wks.find(message).row
            wks_col = self.wks.find('Отправлено?').col
            self.wks.update_cell(wks_row, wks_col, 'Да')

Notifications = NotificationsClass(SheetNotifications, 'notifications')