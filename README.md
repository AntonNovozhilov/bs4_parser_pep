# Проект парсинга PEP/Python Docs
Парсер официальной документации Python с четырьмя режимами работы.

## Описание

Этот парсер собирает данные с официального сайта Python и позволяет:

- **`whats-new`**: получить список статей "What's New" по версиям Python, включая заголовки и авторов.
- **`latest-versions`**: собрать ссылки на документацию всех версий Python и статусы этих версий.
- **`download`**: скачать архив с документацией в формате PDF (A4).
- **`pep`**: проверить статусы документов PEP (Python Enhancement Proposal), сравнивая фактический статус на странице документа с ожидаемым из основного списка. Также считает количество всех и каждого статуса.

## Вывод данных

Результаты можно получить:
- В консоли — в виде красиво отформатированной таблицы с помощью `PrettyTable`.
- В CSV-файле — для последующей обработки или хранения.

## Стек технологий

Проект реализован на Python с использованием следующих библиотек:

- [`requests`](https://pypi.org/project/requests/) + [`requests-cache`](https://pypi.org/project/requests-cache/) — для HTTP-запросов с кешированием
- [`BeautifulSoup4`](https://pypi.org/project/beautifulsoup4/) — для парсинга HTML
- [`tqdm`](https://pypi.org/project/tqdm/) — прогресс-бар для итераций
- [`PrettyTable`](https://pypi.org/project/prettytable/) — форматированный вывод таблиц в консоль
- [`logging`](https://docs.python.org/3/library/logging.html) — встроенное логирование

## Запуск парсера

Убедитесь, что у вас установлен Python 3.10+ и менеджер пакетов pip. Затем выполните следующие шаги:

1. Клонируйте репозиторий или скопируйте проект на другой компьютер.
2. Установите зависимости:
```
pip install -r requirements.txt
```
3. Запустите один из следующих режимов:

### Режимы с выводом в файл (CSV):
```
python main.py whats-new -o file
python main.py latest-versions -o file
python main.py download -o file
python main.py pep -o file
```

### Режимы с выводом в консоль (PrettyTable):
```
python main.py whats-new -o pretty
python main.py latest-versions -o pretty
python main.py download -o pretty
python main.py pep -o pretty
```

### Дополнительные команды:
```
python main.py -h        # Показать справку
python main.py -c        # Очистить кэш
```
## Логирование

Все важные действия логируются: запуск и завершение парсера, ошибки получения данных, расхождения в статусах PEP и пр.

## Автор

Разработано в рамках учебного проекта Yandex Практикум. Автор [Новожилов Антон Алексеевич](https://github.com/AntonNovozhilov)