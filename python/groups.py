import pandas as pd

from sheet import AbstractSheetAdapter

from settings import SheetGroups
from log import Log

class GroupsClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
        if full_df.empty:
            return full_df
        valid = full_df.loc[(full_df['Id'] != None)]
        return valid
    
    def get_all_groups(self) -> list[int]:
        return self.valid['Id'].to_list()

Groups = GroupsClass(SheetGroups, 'groups')