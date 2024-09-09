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
    variant_seen = {}  # Track seen variant options with unique suffix

    for product in json_data.get('products', []):
        try:
            print(f"Processing product: {product.get('title', 'Unknown')}")  # Debug

            # Extract product-specific information
            product_info = {
                "Handle": product.get('handle', ''),
                "Title": product.get('title', ''),
                "Body (HTML)": product.get('body_html', ''),
                "Vendor": product.get('vendor', ''),
                "Product Category": product.get('product_type', ''),
                "Type": product.get('product_type', ''),
                "Tags": ', '.join(product.get('tags', [])),
                "Published": product.get('published_at', ''),
                "Gift Card": 'no',  # Static value
                "Option1 Name": product['options'][0]['name'] if len(product.get('options', [])) > 0 else '',
                "Option2 Name": product['options'][1]['name'] if len(product.get('options', [])) > 1 else '',
                "Option3 Name": product['options'][2]['name'] if len(product.get('options', [])) > 2 else '',
                "Image Src": product.get('images', [{}])[0].get('src', ''),  # Use only the first image
                "Image Position": product.get('images', [{}])[0].get('position', ''),
                "Image Alt Text": '',  # Not available in JSON
            }


            

            product_added = False  # To ensure we only add the product row once

            for variant_index, variant in enumerate(product.get('variants', [])):
                print(f"Processing variant: {variant.get('sku', 'Unknown')}")  # Debug

                # Handle options for variants
                option1 = variant.get('option1') or ''
                option2 = variant.get('option2') or ''
                option3 = variant.get('option3') or ''
                option_values = (option1, option2, option3)
                variant_key = tuple(option_values)

                if variant_key in variant_seen:
                    variant_seen[variant_key] += 1
                else:
                    variant_seen[variant_key] = 1

                unique_suffix = f"_{variant_seen[variant_key]}" if variant_seen[variant_key] > 1 else ''

                # Fetch the variant-specific image if it exists
                variant_image_src = variant.get('featured_image', {}).get('src', product_info['Image Src'])

                # Prepare a single row for the variant
                row = {
                    "Handle": product_info['Handle'],
                    "Title": product_info['Title'] if not product_added else '',
                    "Body (HTML)": product_info['Body (HTML)'] if not product_added else '',
                    "Vendor": product_info['Vendor'] if not product_added else '',
                    "Product Category": product_info['Product Category'] if not product_added else '',
                    "Type": product_info['Type'] if not product_added else '',
                    "Tags": product_info['Tags'] if not product_added else '',
                    "Published": product_info['Published'] if not product_added else '',
                    "Gift Card": product_info['Gift Card'] if not product_added else '',
                    "Option1 Name": product_info['Option1 Name'] if not product_added else '',
                    "Option1 Value": option1 + unique_suffix,
                    "Option2 Name": product_info['Option2 Name'] if not product_added else '',
                    "Option2 Value": option2 + unique_suffix,
                    "Option3 Name": product_info['Option3 Name'] if not product_added else '',
                    "Option3 Value": option3,
                    "Variant SKU": variant.get('sku', '') + unique_suffix,
                    "Variant Grams": variant.get('grams', ''),
                    "Variant Inventory Tracker": "shopify",  # Static value
                    "Variant Inventory Policy": variant.get('inventory_policy', 'deny'),  # Set 'deny' or 'continue'
                    "Variant Fulfillment Service": variant.get('fulfillment_service', 'manual'),  # Default to 'manual'
                    "Variant Price": variant.get('price', ''),
                    "Variant Compare At Price": variant.get('compare_at_price', ''),
                    "Variant Requires Shipping": variant.get('requires_shipping', ''),
                    "Variant Taxable": variant.get('taxable', ''),
                    "Variant Barcode": variant.get('barcode', ''),
                    "Image Src": product_info['Image Src'] if not product_added else '',
                    "Image Position": product_info['Image Position'] if not product_added else '',
                    "Image Alt Text": product_info['Image Alt Text'] if not product_added else '',
                    "Variant Image": variant_image_src,  # Use the variant-specific image or fallback to product image
                    "Variant Weight Unit": '',  # Not available in JSON
                    "Variant Tax Code": '',  # Not available in JSON
                    "Cost per item": '',  # Not available in JSON
                    "Included / Australia": '',  # Custom field placeholder
                    "Price / Australia": '',  # Custom field placeholder
                    "Compare At Price / Australia": '',  # Custom field placeholder
                    "Included / International": '',  # Custom field placeholder
                    "Price / International": '',  # Custom field placeholder
                    "Compare At Price / International": '',  # Custom field placeholder
                    "Status": 'active' if product.get('published_at') else 'draft'  # Set to 'active' if published, otherwise 'draft'
                }

                rows.append(row)

                # Mark that the product row has been added so we don't repeat product-level info for variants
                product_added = True

        except Exception as e:
            error_message = str(e).encode("ascii", errors="replace").decode()
            product_title = product.get('title', 'Unknown').encode("ascii", errors="replace").decode()
            print(f"Error processing product: {product_title}. Error: {error_message}")

    return rows

# Main function to handle pagination and save to CSV files
def main():
    for file_index in range(1, 3):  # Change range to match your required number of files
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
            try:
                df = pd.DataFrame(all_data)

                # Shopify CSV Column Order
                shopify_columns = [
                    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published", 
                    "Gift Card", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", 
                    "Option3 Value", "Variant SKU", "Variant Grams", "Variant Inventory Tracker", 
                    "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price", 
                    "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", 
                    "Image Alt Text", "Variant Image", "Variant Weight Unit", "Variant Tax Code", "Cost per item", 
                    "Included / Australia", "Price / Australia", "Compare At Price / Australia", "Included / International", 
                    "Price / International", "Compare At Price / International", "Status"
                ]

                # Reorder DataFrame columns for Shopify compatibility
                df = df[shopify_columns]

                # Save CSV
                df.to_csv(f'products_data_part_{file_index}.csv', index=False)
                print(f"Data has been successfully written to products_data_part_{file_index}.csv.")
            except Exception as e:
                print(f"Error writing to CSV: {e}")
        else:
            print(f"No data to write for file part {file_index}.")

if __name__ == "__main__":
    main()
