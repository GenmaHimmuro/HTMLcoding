import datetime
from collections import defaultdict
import pandas
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_last_digits(num, digits):
   return num%10**digits


def get_date():
    now = datetime.datetime.now().year
    created_winery = datetime.date(year=1920, month=1, day=1).year
    difference_dates = now - created_winery
    if get_last_digits(num=difference_dates, digits=2) in [10,11,12,13,14]:
        return f"{difference_dates} лет"
    if get_last_digits(num=difference_dates, digits=1) == 1:
        return f"{difference_dates} год"
    if get_last_digits(num=difference_dates, digits=1) in [2,3,4]:
        return f"{difference_dates} года"
    if get_last_digits(num=difference_dates, digits=1) in [5,6,7,8,9,0]:
        return f"{difference_dates} лет"


def get_sorted_wine(filename):
    catalog_wine = pandas.read_excel(io=filename,sheet_name="Лист1",na_values=['N/A', 'NA'],
                                     keep_default_na=False).to_dict(orient="records")
    category_wine = defaultdict(list)
    for wine in catalog_wine:
        category_wine[wine['Категория']].append(wine)
    return category_wine


def get_min_price_and_low_price_offer(filename):
    excel_file = pandas.read_excel(io=filename, sheet_name="Лист1", na_values=['N/A', 'NA'], keep_default_na=False)
    min_price_wines = excel_file.loc[excel_file.groupby('Категория')['Цена'].idxmin()].to_dict(orient="records")
    return min_price_wines


def start_server():
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


def main():
    filename = 'wine3.xlsx'
    env = Environment(loader=FileSystemLoader('.'), autoescape=select_autoescape(['html', 'xml']))
    template = env.get_template('template.html')
    rendered_page = template.render(years_old=get_date(), wines=get_sorted_wine(filename),
                                    min_price=get_min_price_and_low_price_offer(filename))

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    start_server()


if __name__ == "__main__":
    main()

