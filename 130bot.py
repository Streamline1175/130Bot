import discord
from discord.ext import commands
import gspread
from discord_webhook import DiscordWebhook,DiscordEmbed
import aiohttp
import asyncio
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
from datetime import datetime, date, timedelta
import calendar
import re
import logging
import time
import requests
import statistics

exchangeapi_key = 'xxx' # Create API Key on https://exchangeratesapi.io/ and insert here
base_currency = 'USD'

# Set up logging
logging.basicConfig(filename='script.log', level=logging.DEBUG)

logging.basicConfig(
    level=logging.INFO,  # Set the desired logging level (INFO, DEBUG, etc.)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='firefoxtest.log'  # Specify the log file name
)

# Create an instance of discord.Intents
intents = discord.Intents.default()
intents.message_content=True

# Initialize the bot with the intents parameter
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to create and send a webhook
async def send_webhook(channel, username, content="", embeds=None):
    try:
        # Check if the channel is a TextChannel (ignore other channel types like DMs)
        if isinstance(channel, discord.TextChannel):
            # Check if a webhook with a specific name already exists for the channel
            existing_webhooks = await channel.webhooks()
            webhook_name_to_find = username

            existing_webhook = next(
                (wh for wh in existing_webhooks if wh.name == webhook_name_to_find),
                None
            )

            if existing_webhook:
                # Use the existing webhook
                webhook = existing_webhook
            else:
                # Create a new webhook
                webhook = await channel.create_webhook(name=webhook_name_to_find)

            # Extract the URL from the webhook object
            webhook_url = webhook.url

            # Create a payload with the webhook data
            payload = {
                'content': content,
                'username': username,
                'embeds': embeds
            }

            # Send the payload to the Discord webhook
            response = requests.post(webhook_url, json=payload)
            return response.status_code

    except Exception as e:
        print(f"An error occurred while sending the webhook: {str(e)}")
    return None

### Return back item info ###
async def scrape_item_info(ctx, string_search):
    # Start a loading indicator
    loading_message = await ctx.send("Processing Results...")
    
    # Create a logger
    logger = logging.getLogger(__name__)
    
    service = Service(executable_path='/usr/bin/geckodriver')
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    options.log.level = "trace"
    
    # Set the custom user-agent string
    custom_user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
    options.set_preference("general.useragent.override", custom_user_agent)
    
    # Set the page load strategy to 'normal'
    options.set_preference("webdriver.load.strategy", "normal")
    options.set_preference("network.cookie.cookieBehavior", 0)
    options.set_preference("javascript.enabled", True)
    
    # Disable content blocking by setting preferences
    options.set_preference("privacy.trackingprotection.enabled", False)
    options.set_preference("privacy.trackingprotection.fingerprinting.enabled", False)
    options.set_preference("privacy.trackingprotection.cryptomining.enabled", False)
    options.set_preference("privacy.trackingprotection.socialtracking.enabled", False)
    options.set_preference("devtools.console.stdout.chrome", True)
    options.set_preference("devtools.console.stdout.content", True)
    options.set_preference("dom.max_script_run_time", 30)
    options.set_preference("dom.max_chrome_script_run_time", 30)
    options.set_preference("dom.ipc.plugins.timeoutSecs", 30)
    options.set_preference("network.http.sendRefererHeader", 0)
    options.set_preference("browser.contentblocking.category", "")
    
    driver = webdriver.Firefox(service=service, options=options)

    search_url = "https://130point.com/sales/"
    
    searching = string_search.strip('"')
    print(f"\nSearch String: \"{searching}\"\n")
    
    try:
        # Navigate to 130point landing sales page
        driver.get(search_url)
        #time.sleep(5)
    
        # Find the search bar to enter in string of item to lookup
        wait = WebDriverWait(driver, 10)
        
        try:
            # Find the "ACCEPT" button by its ID
            accept_button = driver.find_element(By.ID, "cookie_action_close_header")

            # Click the "ACCEPT" button to dismiss the cookie notification
            accept_button.click()
        except Exception as e:
            # Handle exceptions if the button is not found
            print(f"An error occurred: {str(e)}")
        
        time.sleep(7)
        
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'searchBar')))
        logger.info('Made it to Search Bar!')
        search_field.send_keys(searching)
        time.sleep(5)
        
        # Submit search string 130Point
        submit_button = driver.find_element(By.XPATH, '/html/body/div[6]/div[3]/div/div[2]/div/div[2]/div[5]/div[2]/div/div/div/div[10]/div[2]/button')
        submit_button.click()
        #time.sleep(3)
    
        # Find the password input field and enter your password
        # password_field = wait.until(EC.presence_of_element_located((By.ID, 'password')))  # Replace with the actual ID
        # logger.info('Made it to Password entry!')
        # password_field.send_keys(password)
    
        # Wait for a few seconds (adjust as needed) to allow the page to load
        #search_results = driver.find_element(By.XPATH, '/html/body/div[6]/div[3]/div/div[2]/div/div[2]/div[9]/div[2]/div/div/div/div/div')
        #time.sleep(15)
        
        # Increase the initial timeout
        initial_timeout = 30
        
        try:
            # Wait for the search results to load
            #time.sleep(10)
            search_results = WebDriverWait(driver, initial_timeout).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/div/div[2]/div/div[2]/div[9]/div[2]/div/div/div/div"))
            )
        
            # Create a list to store item data
            items = []
            
            # Create lists to store "Best Offer Accepted" values and "Sale Date" values
            converted_best_offer_values = []
            best_offer_values = []
            sale_dates = []
            
            # Add a counter to keep track of processed items
            total_items_processed = 0
            
            while True:
                try:
                    # Scroll to the bottom of the page to trigger more item loading
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    # Give the page some time to load more items (you can adjust this delay as needed)
                    await asyncio.sleep(8)
                
                    # Find all rows with class "word-break" within the search_results element
                    item_rows = search_results.find_elements(By.XPATH, "//tr[starts-with(@id, 'row')]")
                    
                    # Check if there are any item rows
                    if not item_rows:
                        print("No matching items found.")
                        await loading_message.delete()
                        await ctx.send(f"No matching items found for Search Term - `{searching}`")
                        break
            
                    # Check if the first item row contains the message indicating fewer search terms
                    if "The following results match fewer search terms" in item_rows[0].text:
                        # Skip the first row and continue with the rest of the data
                        item_rows = item_rows[1:]
                    for item_row in item_rows[total_items_processed:]:
                        # Add a counter increment for each item processed
                        total_items_processed += 1
                    
                        # Extract the best offer accepted, if available
                        if "Number of Bids" in item_row.text:
                            try:
                                bids_info = item_row.find_element(By.XPATH, ".//b[text()='Sale Price: ']/following-sibling::a/span[@class='bidLink']")
                                num_bids = bids_info.text
                                best_offer_accepted = num_bids
                                best_offer_values.append(best_offer_accepted)
                            except:
                                best_offer_accepted = "N/A"
                        else:
                            try:
                                # Use BeautifulSoup to parse the HTML content of the item_row
                                soup = BeautifulSoup(item_row.get_attribute("outerHTML"), 'html.parser')
                    
                                # Locate the "Best Offer Accepted" value using CSS selectors
                                best_offer_elem = soup.select_one(".ebayBestOfferAccepted input[type='submit']")
                    
                                if best_offer_elem:
                                    best_offer_accepted = best_offer_elem['value']
                    
                                    if "USD" not in best_offer_accepted:
                                        value_parts = best_offer_accepted.split()
                                        if len(value_parts) == 2:
                                            original_value = float(value_parts[0].replace(',', ''))  # Convert to float
                                            original_currency = value_parts[1]
                    
                                            # Use the exchange rate API to get the exchange rate for original_currency to USD
                                            response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{base_currency}', params={'apikey': exchangeapi_key})
                                            data = response.json()
                                            exchange_rate = data['rates'].get(original_currency)
                    
                                            if exchange_rate is not None:
                                                # Convert the value to USD
                                                usd_value = original_value / exchange_rate
                                                best_offer_accepted = f"{usd_value:.2f} USD"
                                            else:
                                                print(f"Unable to get the exchange rate for {original_currency}")
                                        else:
                                            print("Invalid format: unable to split the combined value.")
                                            best_offer_accepted = "N/A"
                                    else:
                                        best_offer_accepted = f"{best_offer_accepted}"
                                else:
                                    best_offer_accepted = "N/A"
                    
                                # Append "Best Offer Accepted" value to the list
                                best_offer_values.append(best_offer_accepted)
                    
                            except Exception as e:
                                best_offer_accepted = "N/A"
                                print(f"An error occurred: {str(e)}")
                    
                        # Extract the sale date and append it to the list
                        sale_date_elem = item_row.find_element(By.XPATH, ".//span[@class='date-break']")
                        sale_date_text = sale_date_elem.text
                        sale_date_parts = sale_date_text.split(': ')
                        if len(sale_date_parts) == 2:
                            sale_date = sale_date_parts[1]
                            sale_dates.append(sale_date)
                    
                    # Initialize an empty list to store converted values
                    converted_best_offer_values = []
                    
                    #print(best_offer_values)
                    
                    # Outside the loop, initialize a set to keep track of processed item indexes
                    processed_indexes = set()
                    
                    # Inside the loop where you process items
                    for idx, value in enumerate(best_offer_values):
                        if idx not in processed_indexes:
                            if value != "N/A":
                                try:
                                    # Remove commas from the value
                                    value = value.replace(',', '')
                                
                                    # Extract the dollar amount from the value
                                    dollar_amount_match = re.search(r'([\d.]+) USD', value)
                                    if dollar_amount_match:
                                        dollar_amount_str = dollar_amount_match.group(1)
                                        # Convert the dollar amount to a float
                                        dollar_amount = float(dollar_amount_str)
                                        converted_best_offer_values.append(dollar_amount)
                                        #print(f"Processed item {idx + 1} - Extracted dollar amount: ${dollar_amount:.2f}")
                                    else:
                                        print(f"Processed item {idx + 1} - Invalid format: unable to extract dollar amount from value: {value}")
                                except ValueError as e:
                                    print(f"Processed item {idx + 1} - Error converting value to float: {str(e)}")
                                except Exception as e:
                                    print(f"Processed item {idx + 1} - An error occurred: {str(e)}")
                            else:
                                print(f"Processed item {idx + 1} - Value is 'N/A', skipping.\n")
                            
                            # Add the processed index to the set
                            processed_indexes.add(idx)

                    # After processing all items
                    #print(f"Total number of items processed: {total_items_processed}")

                    # Check if there are valid converted values
                    if converted_best_offer_values:
                        min_value = min(converted_best_offer_values)
                        max_value = max(converted_best_offer_values)
                        median_value = statistics.median(converted_best_offer_values)
                    else:
                        min_value = max_value = median_value = "N/A"
                        
                    # After collecting all the item prices in the 'converted_best_offer_values' list
                    if converted_best_offer_values:
                        average_price = sum(converted_best_offer_values) / len(converted_best_offer_values)
                    else:
                        average_price = 0  # Handle the case when no valid prices are found
                    
                    # Function to parse dates in 'Sep 27 2023' format into 'mm/dd/yyyy' format
                    def parse_date(date_string):
                        formats = ['%b %d %Y', '%m/%d/%Y']  # Add more formats as needed
                        
                        for format in formats:
                            try:
                                date_object = datetime.strptime(date_string, format)
                                formatted_date = date_object.strftime('%m/%d/%Y')
                                return formatted_date
                            except ValueError:
                                pass
                        
                        return "N/A"
                    
                    # Find the most recent and oldest "Sale Date"
                    if sale_dates:
                        # Convert sale_dates to 'mm/dd/yyyy' format using parse_date function
                        formatted_sale_dates = [parse_date(date) for date in sale_dates]
                        most_recent_date = max(formatted_sale_dates, key=lambda x: time.strptime(x, '%m/%d/%Y'))
                        oldest_date = min(formatted_sale_dates, key=lambda x: time.strptime(x, '%m/%d/%Y'))
                    else:
                        most_recent_date = oldest_date = "N/A"
                    
                    # Convert sale_dates to datetime objects
                    sale_date_objects = [parse_date(date) for date in sale_dates]
                    date_objects = [datetime.strptime(date_str, '%m/%d/%Y').date() for date_str in sale_date_objects]
                    sale_date_objects = date_objects
                    
                    # Get the current month and previous month
                    current_month = datetime.now().month
                    previous_month = current_month - 1 if current_month > 1 else 12  # Handle January as previous December

                    # Define today.date() as a datetime.date object
                    today_date = date.today()
                    previous_year = today_date.year - 1
                    current_year = today_date.year
                    
                    # Define current_month_start and previous_month_start as datetime.date objects
                    current_month_start = date(current_year, current_month, 1)
                    previous_month_start = date(current_year, previous_month, 1)
                    previous_month_end = current_month_start - timedelta(days=1)
                    
                    # Define sale_prices by extracting sale prices from HTML elements
                    sale_prices = converted_best_offer_values  # Initialize an empty list to store sale prices
                    
                    # Initialize variables to store calculated values
                    current_month_average_price = 0
                    previous_month_average_price = 0
                    current_month_total_sales = 0
                    previous_month_total_sales = 0
                    
                    try:
                        # Filter items for the current and previous months using parse_date
                        current_month_items = [(date, price) for date, price in zip(sale_date_objects, sale_prices) if current_month_start <= date <= today_date]
                        previous_month_items = [(date, price) for date, price in zip(sale_date_objects, sale_prices) if previous_month_start <= date <= previous_month_end]
                    
                        # Calculate the total sales and average price for the current month
                        current_month_sales = [price for _, price in current_month_items]
                        current_month_total_sales = len(current_month_sales)
                        if current_month_total_sales > 0:
                            current_month_average_price = sum(current_month_sales) / current_month_total_sales
                        else:
                            current_month_average_price = 0
                            current_month_total_sales = 0
                    
                        # Calculate the total sales and average price for the previous month
                        previous_month_sales = [price for _, price in previous_month_items]
                        previous_month_total_sales = len(previous_month_sales)
                        if previous_month_total_sales > 0:
                            previous_month_average_price = sum(previous_month_sales) / previous_month_total_sales
                        else:
                            previous_month_average_price = 0
                            previous_month_total_sales = 0
                    
                    except Exception as e:
                        print(f"An error occurred during date filtering and calculation: {str(e)}")
                    
                    # Calculate the change in sales and average price
                    sales_change = current_month_total_sales - previous_month_total_sales
                    avg_price_change = current_month_average_price - previous_month_average_price
                    
                    # Calculate the percentage change, handling division by zero
                    if previous_month_total_sales != 0:
                        sales_change_percentage = (sales_change / previous_month_total_sales) * 100
                    else:
                        sales_change_percentage = 0  # Set to 0 if previous_month_total_sales is 0
                    
                    if previous_month_average_price != 0:
                        avg_price_change_percentage = (avg_price_change / previous_month_average_price) * 100
                    else:
                        avg_price_change_percentage = 0  # Set to 0 if previous_month_average_price is 0
                    
                    # Define the current date
                    current_date = datetime.now().date()
                    
                    # Calculate the start date for the current week
                    current_week_start = current_date - timedelta(days=current_date.weekday())
                    
                    # Create a list to store data for each week
                    weekly_data = []
                    
                    # Calculate data for the last 4 weeks, including the current week
                    for i in range(4):
                        # Calculate the start and end dates for the current week
                        week_start = current_week_start - timedelta(weeks=3 - i)
                        week_end = week_start + timedelta(days=6)
                    
                        # Filter items for the current week
                        week_items = [(date, price) for date, price in zip(sale_date_objects, sale_prices) if week_start <= date <= week_end]
                    
                        # Calculate the total sales and average price for the week
                        week_sales = [price for _, price in week_items]
                        week_total_sales = len(week_sales)
                        if week_total_sales > 0:
                            week_average_price = sum(week_sales) / week_total_sales
                        else:
                            week_average_price = 0
                    
                        # Calculate the difference from the previous week (if available)
                        if weekly_data:
                            previous_week_data = weekly_data[-1]
                            price_difference = week_average_price - previous_week_data["average_price"]
                            if previous_week_data["average_price"] != 0:
                                percentage_difference = (price_difference / previous_week_data["average_price"]) * 100
                            else:
                                percentage_difference = 0
                        else:
                            price_difference = 0
                            percentage_difference = 0
                    
                        # Store data for the current week
                        weekly_data.append({
                            "start_date": week_start.strftime('%m/%d/%Y'),
                            "end_date": week_end.strftime('%m/%d/%Y'),
                            "total_sales": week_total_sales,
                            "average_price": week_average_price,
                            "price_difference": price_difference,
                            "percentage_difference": percentage_difference
                        })
                    
                    # Reverse the list to display the current week at the top
                    weekly_data = weekly_data[::-1]
                    
                    # Print the total number of items processed
                    print(f"Total items processed: {total_items_processed}")
                    
                    # Print Min, Max, Median, Most Recent Date, and Oldest Date
                    print(f"Min Best Offer Accepted: {min_value:.2f} USD")
                    print(f"Max Best Offer Accepted: {max_value:.2f} USD")
                    print(f"Median Best Offer Accepted: {median_value:.2f} USD")
                    print(f"Average Best Offer Accepted Price: ${average_price:.2f} USD")
                    print(f"Most Recent Sale Date: {most_recent_date}")
                    print(f"Oldest Sale Date: {oldest_date}\n")
                    
                    print(f"Current Month Avg (Sales): ${current_month_average_price:.2f} USD ({current_month_total_sales})")
                    print(f"Previous Month Avg (Sales): ${previous_month_average_price:.2f} USD ({previous_month_total_sales})")
                    print(f"Change in Sales: {sales_change_percentage:.2f}%")
                    print(f"Change in Avg Price: {avg_price_change_percentage:.2f}%\n")
                    
                    for i, week_data in enumerate(weekly_data):
                        print(f"Week {i + 1} ({week_data['start_date']} - {week_data['end_date']}):")
                        print(f"Total Sales: {week_data['total_sales']} sales")
                        print(f"Average Price: ${week_data['average_price']:.2f} USD")
                        print(f"Price Difference from Previous Week: ${week_data['price_difference']:.2f} USD")
                        print(f"Percentage Difference from Previous Week: {week_data['percentage_difference']:.2f}%\n")
                    
                    print("All Statistics Completed Successfully")
                    
                    # Get the channel where the command was invoked
                    channel = ctx.channel
                    
                    # Define the username for the webhook
                    webhook_username = "130 Bot"
                        
                    # Create a payload with the embed data
                    content = 'Item Data Summary Pt 1'  # 'content' should be a string
                    embeds = [
                        {
                            'title': 'Data Summary',  # Set an appropriate title for the embed
                            'fields': [
                                {'name': 'Search String', 'value': str(searching), 'inline': True},
                                {'name': 'Total Items Processed', 'value': str(total_items_processed), 'inline': True},
                                {'name': 'Min Best Offer Accepted', 'value': f"${min_value:.2f} USD", 'inline': True},
                                {'name': 'Max Best Offer Accepted', 'value': f"${max_value:.2f} USD", 'inline': True},
                                {'name': 'Median Best Offer Accepted', 'value': f"${median_value:.2f} USD", 'inline': True},
                                {'name': 'Average Best Offer Accepted Price', 'value': f"${average_price:.2f} USD", 'inline': True},
                                {'name': 'Most Recent Sale Date', 'value': most_recent_date, 'inline': True},
                                {'name': 'Oldest Sale Date', 'value': oldest_date, 'inline': True},
                                {'name': 'Current Month Avg (Sales)', 'value': f"${current_month_average_price:.2f} USD ({current_month_total_sales} sales)", 'inline': True},
                                {'name': 'Previous Month Avg (Sales)', 'value': f"${previous_month_average_price:.2f} USD ({previous_month_total_sales} sales)", 'inline': True},
                                {'name': 'Change in Sales Percentage', 'value': f"{sales_change_percentage:.2f}%", 'inline': True},
                                {'name': 'Change in Avg Price Percentage', 'value': f"{avg_price_change_percentage:.2f}%", 'inline': True}
                            ]
                        }
                    ]
                    
                    # Create a payload with the weekly info embed data
                    embeds_weekly = []

                    for i, week_data in enumerate(weekly_data):
                        weekly_embed = {
                            'title': f'Week {i + 1} ({week_data["start_date"]} - {week_data["end_date"]})',
                            'fields': [
                                {'name': 'Total Sales', 'value': f'{week_data["total_sales"]} sales', 'inline': True},
                                {'name': 'Average Price', 'value': f'${week_data["average_price"]:.2f} USD', 'inline': True},
                                {'name': 'Price Difference from Previous Week', 'value': f'${week_data["price_difference"]:.2f} USD', 'inline': True},
                                {'name': 'Percentage Difference from Previous Week', 'value': f'{week_data["percentage_difference"]:.2f}%', 'inline': True}
                            ]
                        }
                        embeds_weekly.append(weekly_embed)
                    
                    # After processing all items, you can remove the loading indicator
                    await loading_message.delete()
                    
                    # Send the payload to the Discord webhook
                    response_code = await send_webhook(channel, webhook_username, embeds=embeds)
                    response_code_weekly = await send_webhook(channel, webhook_username, embeds=embeds_weekly)
                    break
                     
                except NoSuchElementException:
                    logger.warning("No more items found. Exiting loop.")
                    break
        
        except Exception as e:
            logger.error(f'An error occurred while waiting for search results: {str(e)}')

    
    finally:
        # Close the browser window
        driver.quit()

# Modify the iteminfo command to call the async function
@bot.command()
async def item(ctx, *, string_search: str):
    if not string_search:
        await ctx.send("Please provide a search string. If it contains spaces, enclose it in double quotes.")
        return
    try:
        # Execute the web scraping function asynchronously
        await scrape_item_info(ctx, string_search)
    except Exception as e:
        # Handle any exceptions here, e.g., send an error message to Discord
        await ctx.send(f"An error occurred: {str(e)}")

# Insert Discord Bot Key Below, retrieved from - https://discord.com/developers/applications/<Application ID>/bot
bot.run('xxx')