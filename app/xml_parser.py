import xmltodict
from datetime import datetime


def parse_sales_data(xml_content):
    sales = []
    data = xmltodict.parse(xml_content)
    date = datetime.strptime(data['sales_data']['@date'], "%Y-%m-%d")
    products = data['sales_data']['products']['product']

    for product in products:
        sales.append({
            "product_id": int(product['id']),
            "name": product['name'],
            "quantity": int(product['quantity']),
            "price": float(product['price']),
            "category": product['category'],
            "date": date
        })
    return sales
