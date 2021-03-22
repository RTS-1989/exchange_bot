from dataclasses import dataclass
from emoji import emojize


@dataclass(frozen=True)
class Messages:
    test: str = 'Привет, {name}! Работаю.'
    btn_ec_today: str = 'Данные по курсам валют на сегодня'
    btn_config: str = f"{emojize(':memo:')} Настройки"
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
    config: str = "Сейчас выбраны:\n{currencies}"
    btn_back: str = "<- Назад"
    btn_go: str = "Вперед ->"
    btn_save: str = "Сохранить"
    config_btn_edit: str = "Изменить"
    config_btn_delete: str = "Удалить данные"
    data_delete: str = "Данные успешно удалены"
    set_currencies: str = "Выбери 3 валюты для отслеживания.\nВыбраны:\n{currencies}"
    main: str = "Что будем делать?"
    db_saved: str = "Настройки сохранены"
    cb_not_saved: str = "Валюты не выбраны"
    cb_limit: str = "Превышен лимит. Максимум 3 Валюты."
    results: str = "Все результаты за сегодня\n{last_currencies}"
    no_results: str = "Нет данных по курсам валют"
    update_results: str = "Обновить результаты"
    cb_updated: str = f"{emojize(':white_heavy_check_mark:')} Готово"
    unknown_text: str = "Ничего не понятно, но очень интересно.\nПопробуй команду /help"
    fetch_error: str = 'Ошибка получения данных, попробуйте позже.'


msg = Messages()
