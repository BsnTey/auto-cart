import random


def get_product_values(json):
    if not json:
        return None, None

    products = json.get("products", [])
    product_id, product_ware_id = None, None

    while products:
        product = random.choice(products)
        products.remove(product)

        product_price = product.get("price", {})
        discount_rate = product_price.get("discountRate")

        if discount_rate == 0:
            product_sizes = product.get("sizes", [])
            product_id = product.get("productId")

            while product_sizes:
                size = random.choice(product_sizes)
                product_sizes.remove(size)
                is_available_online = size.get("isAvailableOnline")
                if is_available_online:
                    product_ware_id = size.get("id")
                    break

        if product_id and product_ware_id:
            break

    return product_id, product_ware_id
