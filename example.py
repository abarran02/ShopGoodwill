from src.ShopGoodwill import ShopGoodwill

if __name__ == "__main__":
    sg = ShopGoodwill(filters={'searchOneCentShippingOnly': True}, max_results=1, include_details=True)
    for i in range(len(sg.items)):
        print(sg.items[i].item_details)
