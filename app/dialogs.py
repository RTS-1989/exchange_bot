from dataclasses import dataclass


@dataclass(frozen=True)
class Messages:
    test: str = 'Привет, {name}! Работаю.'


msg = Messages()

# greetings_messages = ['привет', 'приветствую', 'здравствуйте', 'салют']

start_new_user: str = "Привет. Я могу сообщать тебе данные по курсам валют."
start_current_user: str = "Привет. С возвращением! " \
                          "Используй команды или меню внизу для продолжения."
help: str = """
Этот бот получает данные о стоимости валюты за последние 2 дня,
а также на указанную в запросе дату.
Включая режим LIVE.
- Что бы выбрать/изменить валюту нажмите "Настройки".
- Для проверки двнных на сегодняшний день нажмите "ec_today".
"""

currency_row: str = "{i}. {name}"
config: str = f"Сейчас выбраны:\n{currencies}"
btn_back: str = "<- Назад"
btn_go: str = "Вперед ->"
btn_save: str = "Сохранить"
config_btn_edit: str = "Изменить"
config_btn_delete: str = "Удалить данные"
data_delete: str = "Данные успешно удалены"
set_leagues: str = "Выбери 3 лиги для отслеживания.\nВыбраны:\n{currencies}"
main: str = "Что будем делать?"
db_saved: str = "Настройки сохранены"
cb_not_saved: str = "Валюты не выбраны"
cb_limit: str = "Превышен лимит. Максимум 3 Валюты."
