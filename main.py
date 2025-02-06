import datetime
from collections import defaultdict
import pandas
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
import argparse


def get_last_digits(num, digits):
   return num%10**digits


def get_age_of_winery(now):
    date_of_est_winery = datetime.date(year=1920, month=1, day=1).year
    return now - date_of_est_winery


def find_right_word(difference_dates):
    if get_last_digits(num=difference_dates, digits=2) in [10,11,12,13,14]:
        return f"{difference_dates} лет"
    if get_last_digits(num=difference_dates, digits=1) == 1:
        return f"{difference_dates} год"
    if get_last_digits(num=difference_dates, digits=1) in [2,3,4]:
        return f"{difference_dates} года"
    if get_last_digits(num=difference_dates, digits=1) in [5,6,7,8,9,0]:
        return f"{difference_dates} лет"


def get_sorted_wine(excel_file):
    dict_with_catalog_wine = excel_file.to_dict(orient="records")
    divide_categories_wines = defaultdict(list)
    for wine in dict_with_catalog_wine:
        divide_categories_wines[wine['Категория']].append(wine)
    return divide_categories_wines


def get_min_price_offer(excel_file):
    min_price_wines = excel_file.nsmallest(1,'Цена').to_dict(orient="records")
    return min_price_wines


def get_good_offer(excel_file):
    good_offer_wine = excel_file[excel_file['Акция'].isin(['Выгодное предложение'])].to_dict(orient="records")
    return good_offer_wine


def start_server():
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        description="Укажите имя Excel таблицы с информацией о винах для сайта винодельни")
    parser.add_argument(
        "filename", help="Excel файл")
    args = parser.parse_args()
    filename = args.filename

    now = datetime.datetime.now().year
    difference_dates = get_age_of_winery(now)
    right_word = find_right_word(difference_dates)

    excel_file = pandas.read_excel(io=filename, sheet_name="Лист1", na_values=['N/A', 'NA'], keep_default_na=False)
    env = Environment(loader=FileSystemLoader('.'), autoescape=select_autoescape(['html', 'xml']))
    template = env.get_template('template.html')
    rendered_page = template.render(years_old=right_word, wines=get_sorted_wine(excel_file),
                                    min_price = get_min_price_offer(excel_file), good_offer = get_good_offer(excel_file))

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    start_server()


if __name__ == "__main__":
    main()

