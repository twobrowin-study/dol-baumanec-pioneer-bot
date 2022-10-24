import pandas as pd

from sheet import AbstractSheetAdapter

from settings import SheetCommands
from log import Log

COMMAND_START = 'start'
COMMAND_HELP = 'help'
COMMAND_END = 'end'
COMMAND_GETINFO = 'getinfo'
COMMAND_UNREGISTER = 'unregister'
COMMAND_REREGISTER = 'reregister'
COMMAND_REGISTER = 'register'
COMMAND_ALL_SONGS = 'songs_end'

class CommandsClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
        valid = full_df.loc[
            (full_df['Команда'] != '') &
            (full_df['Показывать в списке команд бота?'] != '') &
            (full_df['Краткое описание'] != '') &
            (
                (full_df['Ответ (бота)'] != '') |
                (full_df['Ответ если пользователь зарегистрирован'] != '')
            )
        ]
        return valid
    
    def get_commands_descriptions(self) -> list[tuple[str, str]]:
        return list(self.valid.loc[
            self.valid['Показывать в списке команд бота?'] == 'Да'
        ][['Команда', 'Краткое описание']].itertuples(index=False, name=None))
    
    def get_responce_to_command(self, command: str) -> str:
        for _,row in self.valid.loc[self.valid['Команда'] == command].iterrows():
            return row['Ответ (бота)']
        return ""
    
    def get_responce_to_registered_user(self, command: str) -> str:
        for _,row in self.valid.loc[self.valid['Команда'] == command].iterrows():
            return row['Ответ если пользователь зарегистрирован']
        return ""
        
Commands = CommandsClass(SheetCommands, 'commands')