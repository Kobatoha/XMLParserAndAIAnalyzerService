import httpx
from app.xml_parser import parse_sales_data
from app.llm_client import generate_report
from app.models import Sale, Report, SessionLocal
from celery import Celery
import os
from datetime import datetime

celery = Celery(__name__, broker="redis://redis:6379/0")


@celery.task
def process_sales_data():
    url = "https://example.com/sales.xml"
    response = httpx.get(url)

    if response.status_code != 200:
        print("Failed to fetch XML data")
        return

    sales_data = parse_sales_data(response.text)
    db = SessionLocal()

    # Сохранение данных в БД
    for sale in sales_data:
        db.add(Sale(**sale))
    db.commit()

    # Генерация промпта
    total_revenue = sum(sale["quantity"] * sale["price"] for sale in sales_data)
    top_products = sorted(sales_data, key=lambda x: x["quantity"], reverse=True)[:3]
    top_products_str = ", ".join([f"{p['name']} ({p['quantity']})" for p in top_products])
    categories = {sale["category"] for sale in sales_data}

    prompt = f"""
    Проанализируй данные о продажах за {datetime.now().date()}:
    1. Общая выручка: {total_revenue}
    2. Топ-3 товара по продажам: {top_products_str}
    3. Категории: {', '.join(categories)}
    Составь краткий аналитический отчет с выводами и рекомендациями.
    """

    # Получение отчета от LLM
    report_content = generate_report(prompt)

    # Сохранение отчета в БД
    report = Report(date=datetime.now().date(), content=report_content)
    db.add(report)
    db.commit()
    db.close()
