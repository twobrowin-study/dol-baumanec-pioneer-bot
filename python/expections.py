import pandas as pd

from sheet import AbstractSheetAdapter

from telegram import ReplyKeyboardMarkup

from settings import SheetExpections
from log import Log

class ExpectionsClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
        if full_df.empty:
            return full_df
        valid = full_df.loc[(full_df['Ответ'] != None)]
        return valid
    
    def get_keyboard_markup(self):
        nrows = self.valid.shape[0]
        markup = []
        for idx in range(0,nrows,2):
            desriptions = list(self.valid.iloc[idx:idx+2]['Ответ'].values)
            markup.append(desriptions)
        return ReplyKeyboardMarkup(markup)

Expections = ExpectionsClass(SheetExpections, 'expections')