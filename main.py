import pandas as pd
from pathlib import Path


def main():
    print('=== Анализ продаж по SKU ===\n')

    # Получаем путь к папке с исходным файлом
    folder = Path(
        input('Введите путь к папке с исходным файлом: ').strip().strip('"')
    )

    # Проверяем существование папки
    if not folder.is_dir():
        print('\nОшибка: указанная папка не найдена.')
        return

    # Получаем название исходного файла
    file_name = input('\nВведите название CSV-файла: ').strip().strip('"')

    # Проверяем и добавляем расширение .csv при необходимости
    if not file_name.lower().endswith('.csv'):
        file_name += '.csv'

    input_file = folder / file_name

    # Проверяем наличие файла
    if not input_file.is_file():
        print('\nОшибка: файл не найден в указанной папке.')
        return

    try:
        print('\nОбработка данных...')

        # Считываем файл
        df = pd.read_csv(input_file)

        # Приводим order_date к datetime
        df['order_date'] = pd.to_datetime(
            df['order_date'],
            errors='coerce',
            format='%Y-%m-%d'
        )

        # Удаляем полные дубликаты строк
        df = df.drop_duplicates()

        # Нормализуем статусы
        df['status'] = df['status'].str.strip().str.lower()
        df['status'] = df['status'].replace('canceled', 'cancelled')

        # Рассчитываем выручку только по доставленным заказам
        df['revenue'] = (
            df['quantity'] * df['price']
        ).where(df['status'] == 'delivered', 0)

        # Агрегируем данные по SKU и дате
        df_daily = (
            df.groupby(['sku', 'order_date'], as_index=False)
            .agg(
                orders=('order_id', 'nunique'),
                revenue=('revenue', 'sum')
            )
            .sort_values(['sku', 'order_date'])
        )

        # Сохраняем результат в исходную папку
        output_file = folder / 'daily_by_sku.csv'
        df_daily.to_csv(output_file, index=False)

        print('\nОбработка успешно завершена!')
        print(f'Количество строк в результате: {len(df_daily)}')
        print(f'Файл сохранён: {output_file}')

    except Exception as error:
        print(f'\nОшибка при обработке данных: {error}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nПрограмма прервана пользователем.')

    input('\nНажмите Enter для завершения...')