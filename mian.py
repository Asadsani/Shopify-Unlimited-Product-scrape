import requests
import pandas as pd

# Function to fetch JSON data from a given page number
def fetch_json_data(page):
    url = f"https://ozmobiles.com.au/products.json?per_page=250&page={page}"
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.json()

# Function to process the JSON data and flatten it for DataFrame
def process_json_data(json_data):
    rows = []
    for product in json_data.get('products', []):
        for variant in product.get('variants', []):
            for image in product.get('images', []):
                row = {
                    "Handle": product.get('handle', ''),
                    "Title": product.get('title', ''),
                    "Body (HTML)": product.get('body_html', ''),
                    "Vendor": product.get('vendor', ''),
                    "Type": product.get('product_type', ''),
                    "Tags": ', '.join(product.get('tags', [])),
                    "Published": product.get('published_at', ''),
                    "Option1 Name": product['options'][0]['name'] if len(product.get('options', [])) > 0 else '',
                    "Option1 Value": product['options'][0]['values'][0] if len(product.get('options', [])) > 0 and len(product['options'][0]['values']) > 0 else '',
                    "Option2 Name": product['options'][1]['name'] if len(product.get('options', [])) > 1 else '',
                    "Option2 Value": product['options'][1]['values'][0] if len(product.get('options', [])) > 1 and len(product['options'][1]['values']) > 0 else '',
                    "Option3 Name": product['options'][2]['name'] if len(product.get('options', [])) > 2 else '',
                    "Option3 Value": product['options'][2]['values'][0] if len(product.get('options', [])) > 2 and len(product['options'][2]['values']) > 0 else '',
                    "Variant SKU": variant.get('sku', ''),
                    "Variant Grams": variant.get('grams', ''),
                    "Variant Inventory Tracker": "shopify",  # Static value
                    "Variant Inventory Qty": variant.get('inventory_quantity', ''),
                    "Variant Inventory Policy": variant.get('inventory_policy', ''),
                    "Variant Fulfillment Service": variant.get('fulfillment_service', ''),
                    "Variant Price": variant.get('price', ''),
                    "Variant Compare At Price": variant.get('compare_at_price', ''),
                    "Variant Requires Shipping": variant.get('requires_shipping', ''),
                    "Variant Taxable": variant.get('taxable', ''),
                    "Variant Barcode": variant.get('barcode', ''),
                    "Image Src": image.get('src', ''),
                    "Image Position": image.get('position', ''),
                    "Image Alt Text": '',  # Not available in JSON
                    "Gift Card": 'no',  # Static value
                    "SEO Title": '',  # Not available in JSON
                    "SEO Description": '',  # Not available in JSON
                    "Google Shopping / Google Product Category": '',  # Not available in JSON
                    "Google Shopping / Gender": '',  # Not available in JSON
                    "Google Shopping / Age Group": '',  # Not available in JSON
                    "Google Shopping / MPN": '',  # Not available in JSON
                    "Google Shopping / AdWords Grouping": '',  # Not available in JSON
                    "Google Shopping / AdWords Labels": '',  # Not available in JSON
                    "Google Shopping / Condition": '',  # Not available in JSON
                    "Google Shopping / Custom Product": '',  # Not available in JSON
                    "Google Shopping / Custom Label 0": '',  # Not available in JSON
                    "Google Shopping / Custom Label 1": '',  # Not available in JSON
                    "Google Shopping / Custom Label 2": '',  # Not available in JSON
                    "Google Shopping / Custom Label 3": '',  # Not available in JSON
                    "Google Shopping / Custom Label 4": '',  # Not available in JSON
                    "Variant Image": image.get('src', ''),
                    "Variant Weight Unit": '',  # Not available in JSON
                    "Variant Tax Code": '',  # Not available in JSON
                    "Cost per item": '',  # Not available in JSON
                    "Status": ''  # Not available in JSON
                }
                rows.append(row)
    return rows

# Main function to handle pagination and save to CSV files
def main():
    for file_index in range(1, 3):  # Change the range to match your required number of files
        all_data = []
        start_page = (file_index - 1) * 15 + 1
        end_page = start_page + 14

        for page in range(start_page, end_page + 1):
            print(f"Fetching data from page {page}...")
            try:
                json_data = fetch_json_data(page)
                products = json_data.get('products', [])
                if not products:
                    print(f"No more data found on page {page}.")
                    break
                data = process_json_data(json_data)
                all_data.extend(data)
            except requests.RequestException as e:
                print(f"An error occurred: {e}")
                break

        if all_data:
            # Create a DataFrame and write to CSV
            try:
                df = pd.DataFrame(all_data)
                df.to_csv(f'products_data_part_{file_index}.csv', index=False)
                print(f"Data has been successfully written to products_data_part_{file_index}.csv.")
            except Exception as e:
                print(f"An error occurred while writing to CSV: {e}")
        else:
            print(f"No data to write for file part {file_index}.")

if __name__ == "__main__":
    main()
