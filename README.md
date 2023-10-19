# 130Bot
Webscrapes info from 130point.com based on string value passed via Discord Command and returns informational webhooks.

Run the below command to pull Firefox v90.0 to install:
```shell
# Download firefox version 90.0 for Linux 64-bit
curl -o firefox-90.0.tar.bz2 https://ftp.mozilla.org/pub/firefox/releases/90.0/linux-x86_64/en-US/firefox-90.0.tar.bz2
```
Next run the following commands in this order to install the above downloaded version:
```shell
# Navigate to the directory where the downloaded file is located, if not already in the same directory
cd /path/to/downloaded/directory

# Extract the Firefox archive
tar xjf firefox-90.0.tar.bz2

# Move the extracted Firefox directory to a location where you want to install it
sudo mv firefox /opt/

# Create a symbolic link to the Firefox binary to make it accessible system-wide
sudo ln -s /opt/firefox/firefox /usr/local/bin/

# Now, you can run Firefox by typing 'firefox' in the terminal
# *** Might not work if geckodriver isn't already installed ***
firefox
```

Next we need to download geckodriver v0.30.0 which is required for the Firefox package:
```shell
# Download geckodriver version 0.30.0 for Linux 64-bit
curl -o geckodriver-v0.30.0-linux64.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
```

Then run the following commands in the below order to unzip and set it up:
```shell
# Navigate to the directory where the downloaded geckodriver file is located, if not already in the same directory
cd /path/to/downloaded/directory

# Extract the geckodriver archive
tar xzf geckodriver-v0.30.0-linux64.tar.gz

# Make geckodriver executable and move it to a directory included in your system's PATH
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/
```

Once all steps above are completed you can verify to ensure they were installed correctly:
```shell
:~$ geckodriver --version
geckodriver 0.30.0 (d372710b98a6 2021-09-16 10:29 +0300)

The source code of this program is available from
testing/geckodriver in https://hg.mozilla.org/mozilla-central.

This program is subject to the terms of the Mozilla Public License 2.0.
You can obtain a copy of the license at https://mozilla.org/MPL/2.0/.

:~$ firefox --version
Mozilla Firefox 90.0
```

Next you will need to get an Exchange Rate API Key from this site in order to convert any currency into USD:

https://exchangeratesapi.io/

Once you got your free API key it can be placed within this section of code:
```python
exchangeapi_key = 'xxx' # Create API Key on https://exchangeratesapi.io/ and insert here
```
If you also want to change your base currency to something other than USD that can be modified within the script as well:
```python
base_currency = 'USD'
```
You will then need to head over to the Discord Developers Portal to create a new Application where you will get your Bot Token that is required for this script to be interactable from the command issued in Discord:

1. Got to https://discord.com/developers/applications
2. Click "**New Application**"
3. Name the Bot whatever you want and then submit it
4. On the left sidebar click "**Bot**"
5. Then click "**Reset Token**" and a new one will get generated, make sure to save it and add it into your script at the bottom shown here:
    ```python
    # Insert Discord Bot Key Below, retrieved from - https://discord.com/developers/applications/<Application ID>/bot
    bot.run('xxx')
    ```
6. Then click "**OAuth2**" -> "**URL Generator**" and configure the url as **Scopes**=**bot**
7. Then if this will be in a community/public server you can modify the permissions but all the bot really needs is the ability to:

   a. Manage Webhooks
   
   b. Send Messages

   c. Manage Messages

   d. Read Message History

   e. Read Messages/View Channels

   ```shell
   # Example URL should look like this that is generated
   https://discord.com/api/oauth2/authorize?client_id=<Client/App ID>&permissions=536947712&scope=bot
   ```
8. Once all of that is configured and the bot is authenticated/added to the server then you can execute the script locally or on a server, your choice:
    ```python
    :~$ python3 130bot.py
    ```

Once you see the bot is active within the server it was added to then you can execute the command for the bot to trigger:
```shell
!item <string-value>

# Example
!item pokemon japanese vstar universe booster box
```
The bot will beginning executing and put this message into the server while it is searching and pulling back results:
```shell
Processing Results...
```
If everything runs correctly and it finds results it will send back print statements similar to this in the terminal:
```diff
Search String: "pokemon japanese vstar universe booster box"

Total items processed: 59
Min Best Offer Accepted: 2.75 USD
Max Best Offer Accepted: 1550.00 USD
Median Best Offer Accepted: 96.96 USD
Average Best Offer Accepted Price: $191.17 USD
Most Recent Sale Date: 10/18/2023
Oldest Sale Date: 02/28/2023

Current Month Avg (Sales): $194.28 USD (57)
Previous Month Avg (Sales): $0.00 USD (0)
Change in Sales: 0.00%
Change in Avg Price: 0.00%

Week 1 (10/16/2023 - 10/22/2023):
Total Sales: 33 sales
Average Price: $193.32 USD
Price Difference from Previous Week: $-2.28 USD
Percentage Difference from Previous Week: -1.17%

Week 2 (10/09/2023 - 10/15/2023):
Total Sales: 24 sales
Average Price: $195.60 USD
Price Difference from Previous Week: $195.60 USD
Percentage Difference from Previous Week: 0.00%

Week 3 (10/02/2023 - 10/08/2023):
Total Sales: 0 sales
Average Price: $0.00 USD
Price Difference from Previous Week: $0.00 USD
Percentage Difference from Previous Week: 0.00%

Week 4 (09/25/2023 - 10/01/2023):
Total Sales: 0 sales
Average Price: $0.00 USD
Price Difference from Previous Week: $0.00 USD
Percentage Difference from Previous Week: 0.00%

All Statistics Completed Successfully
```
The webhooks will look like this in discord:
![alt text](https://github.com/Streamline1175/130Bot/blob/main/130bot.JPG "Webhook Sample")

You are now ready to leverage this bot for whatever you want in Discord to get info about any item that sells on eBay!

If you have any requests or enhancements that you want made to this bot let me know or feel free to fork this project and add whatever you want to it!