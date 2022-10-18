from os import environ, getenv

BotToken = environ.get('BOT_TOKEN')
if BotToken == '' or BotToken == None:
    with open('telegram.txt', 'r') as fp:
        BotToken = fp.read()

SheetsAccJson = environ.get('SHEETS_ACC_JSON')
SheetsSecret = './serviceacc.json'
if SheetsAccJson != None and SheetsAccJson != '':
    with open(SheetsSecret, 'w') as fp:
        fp.write(SheetsAccJson)

SheetsName = getenv('SHEETS_NAME', 'Регистрация (Ответы)')

SheetAnswers = getenv('SHEET_ANSWERS', 'Ответы на форму (1)')
SheetGroups = getenv('SHEET_GROUPS', 'Группа для отчётов')
SheetCommands = getenv('SHEET_COMMANDS', 'Команды бота')
SheetNotifications = getenv('SHEET_NOTIFICATIONS', 'Оповещения пользователей по дате и времени')
SheetExpections = getenv('SHEET_EXPECTIONS', 'Варианты ответов на последний вопрос')

SheetUpdateTimeout = int(getenv('SHEET_UPDATE_TIMEOUT', '10'))
NotificationsTimeout = int(getenv('NOTIFICATIONS_TIMEOUT', '10'))
