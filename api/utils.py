import os
import re


def get_api_tokens():
    try:
        from google.colab import userdata
        MS_API_TOKEN = userdata.get('MS_API_TOKEN')
        WB_API_TOKEN = userdata.get('WB_API_TOKEN')
        return MS_API_TOKEN, WB_API_TOKEN
    except ImportError:
        pass

    MS_API_TOKEN = os.getenv('MS_API_TOKEN')
    WB_API_TOKEN = os.getenv('WB_API_TOKEN')

    return MS_API_TOKEN, WB_API_TOKEN


def get_category_dict(wb_client, fbs=True):
    commission = wb_client.get_commission()
    if fbs:
        key = 'kgvpMarketplace'
    else:
        key = 'paidStorageKgvp'
    category_dict = {comm['subjectName']: comm[key] for comm in commission['report']}
    return category_dict


def get_product_id_from_url(url):
    pattern = r'/product/([0-9a-fA-F-]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None


def get_stock_for_bundle(stocks_dict, product):
    product_bundles = product['components']['rows']
    product_stock = 0.0
    for bundle in product_bundles:
        bundle_id = get_product_id_from_url(bundle['assortment']['meta']['href'])
        if bundle_id in stocks_dict:
            p_stock = stocks_dict[bundle_id] // bundle['quantity']
            if p_stock > product_stock:
                product_stock = p_stock
    return product_stock


def get_ms_stocks_dict(ms_client, products):
    print('Получение остатков номенклатуры')
    stocks = ms_client.get_stock()
    stocks_dict = {stock['assortmentId']: stock['quantity'] for stock in stocks}
    wb_stocks_dict = {int(product['code']): get_stock_for_bundle(stocks_dict, product) for product in products}
    return wb_stocks_dict


def get_price_dict(wb_client):
    data = wb_client.get_product_prices()
    # TODO: Добавить возможность получения данных по другим размерам, либо изменить источник
    price_dict = {d['nmID']: {'price': d['sizes'][0]['discountedPrice'], 'discount': d['discount']} for d in data
                  if len(d['sizes']) == 1}
    return price_dict


def get_dict_for_report(products, ms_client, wb_client, fbs=True):
    # TODO: Переписать на асинхронные запросы
    category_dict = get_category_dict(wb_client, fbs=fbs)
    tariffs_logistic_data = wb_client.get_tariffs_for_box()
    ms_stocks_dict = get_ms_stocks_dict(ms_client, products)
    wb_prices_dict = get_price_dict(wb_client)

    return {
        'ms_stocks_dict': ms_stocks_dict,
        'category_dict': category_dict,
        'tariffs_data': tariffs_logistic_data,
        'wb_prices_dict': wb_prices_dict
    }


def create_code_index(elements):
    code_index = {}
    for element in elements:
        code = int(element.get('code'))
        if code:
            code_index[code] = element
    return code_index
