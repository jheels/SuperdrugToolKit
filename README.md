# Superdrug Stock Checker

A simple discord-based multi-purpose bot to assist Superdrug Retail Arbitrage. Able to scrape in-store stock from nearby stores with product SKUs as well as return useful info for product analysis in a clean, simple embed.

## Installation

Install the required dependencies in requirements.txt before running. 

```bash
pip install -r requirements.txt
```

You will need to create a discord bot to your server. Refer to this guide [here](https://discordpy.readthedocs.io/en/stable/discord.html). During step 5, tick _application.commands_ too!

Under the _bot_ scope, tick the following requirements if you are not able to tick _administrator_ by default:

- Read Messages/View Channels
- Send Messages
- Send Messages in Threads
- Embed Links
- Attach Files
- Read Message History
- Use Slash Commands

Once the bot is added to your server, you will need to add the secret token to your list of environment variables. The name of the token must be **SUPERDRUG_SCRAPER_TOKEN** otherwise it will not run.

Here are a step-by-step guide for the respective OS:

- [Windows](https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0)
- [MacOS](https://phoenixnap.com/kb/set-environment-variable-mac#:~:text=Set%20Permanent%20Environment%20Variable
) - Note this may vary dependant on the shell used
- [Linux](https://www.freecodecamp.org/news/how-to-set-an-environment-variable-in-linux/)

Once the above steps are completed, you can run the bot with the command (if you changed the filename replace _main_ with the respective filename)

```bash
python3 main.py
```

The bot should be now able to execute commands in your respective server.

## Usage

The bot operates using Discord's slash commands method. There are currently 2 commands available:

- /info
- /storestockcheck

### /Info

A quick method to scrape necessary data using the product's SKU. Information can be summarised in a snippet below

<img src="https://cdn.discordapp.com/attachments/1133103822735155251/1141497658477912104/image.png" alt="Discord embed containing important product information scraped from a SKU" width="60%" height="40%"/>

Note _SD_ stands for Student Discount [Price].

Quick Links are provided for ease of access to SellerAmp search as well as cashback if you plan to purchase the item.

#### Parameters:
- Code - A 6 digit SKU Code unique to each item. This can be found at the end of each product link or on store labels

### /Storestockcheck

Returns stores instock with the desired product from a top 20 list of nearby stores for the given location. If no stores stock the product or the location is invalid then it will return an error message.

<img src="https://media.discordapp.net/attachments/1133103822735155251/1141495056625315840/image.png?width=1128&height=1228" alt="Discord embed containing store stock information for a given product" width="60%" height="40%"/>

Similar embed style to the previous command but some information is omitted for simplicity. However, that information can still be found via the API link given if necessary. A very useful command whilst on the go and unable to use laptops or other large devices.

#### Parameters:
- Code - A 6 digit SKU Code unique to each item. This can be found at the end of each product link or on store labels
- Location - Can be quite varied in input. Postcodes, names etc. are permissible.

## License

None (Respective copyright laws apply)

