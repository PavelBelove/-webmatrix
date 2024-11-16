# Browser Assistant - Автоматизация работы с браузером через AI

Этот инструмент позволяет автоматизировать рутинные задачи по сбору информации с веб-сайтов с помощью искусственного интеллекта. Программа посещает указанные сайты и отвечает на заданные вопросы, сохраняя результаты в Excel файл.

## Как это работает

1. Вы создаете Excel файл со списком сайтов/компаний для анализа
2. Описываете задачу для AI в текстовом файле (что искать, какие вопросы задавать)
3. Указываете, какие данные хотите получить на выходе
4. Запускаете программу - она автоматически проанализирует все сайты и создаст Excel файл с результатами

## Подготовка файлов

### 1. Входной Excel файл (input.xlsx)
- Создайте таблицу с данными для анализа
- Первая строка должна содержать названия колонок
- Обязательно укажите колонку с URL сайтов
- Можно добавить любые дополнительные колонки (название компании, категория и т.д.)

Пример:
| website | company_name | category |
|---------|-------------|-----------|
| https://example.com | Example Inc | Retail |

### 2. Файл с инструкциями (prompt.txt)
Опишите задачу для AI в этом файле. Важные моменты:
- Используйте переменные из входного файла в фигурных скобках: {website}, {company_name}
- Четко структурируйте инструкции по шагам
- В конце обязательно укажите формат JSON для ответа
- Названия полей в JSON должны совпадать с output_columns.txt

Пример: 