from koreannet.gtin import Search

def main():
    gtin_num = input("Please enter the GTIN (Product Barcode) number: ")

    koreannet = Search(gtin_num)
    result = koreannet.search_gtin()

    if result["product_name"]:
        print("GTIN code: " + result["gtin_code"])
        print("Product name: " + result["product_name"])
    else:
        print(result["message"])

if __name__ == "__main__":
    main()
