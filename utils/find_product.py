from utils.get_product_values import get_product_values




async def find_product_catalog(api_requests):
    product_id, product_ware_id = None, None
    for i in range(4):
        status_code, response_body = await api_requests.catalog_api()
        if status_code != 200:
            continue

        product_id, product_ware_id = get_product_values(response_body)
        if not product_id:
            continue
        else:
            break
    return product_id, product_ware_id


async def find_product_view(api_requests, product_id):
    status_code, response_body = await api_requests.product_view(product_id)

    if status_code != 200:
        return False

    marks = response_body.get("marks")
    if "BONUSNA" not in marks:
        return True
    return False



    # while True:
    #     for i in range(4):
    #         status_code, response_body = await api_requests.catalog_api()
    #         if status_code != 200:
    #             continue
    #
    #         product_id, product_ware_id = get_product_values(response_body)
    #         if not product_id:
    #             continue
    #         else:
    #             break
    #
    #     if not product_id:
    #         continue
    #
    #     if txt.check_product_number(product_id):
    #         continue
    #
    #     status_code, response_body = await api_requests.product_view(product_id)
    #
    #     if status_code != 200:
    #         continue
    #
    #     marks = response_body.get("marks")
    #     if "BONUSNA" not in marks:
    #         break
    #
    # return product_id