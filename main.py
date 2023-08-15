import httpx
import discord
import asyncio
import os
from typing import Dict, Any, TypeAlias
from discord import app_commands


headers = {
    'cache-control': 'no-cache',
    'dnt': '1',
    'sec-ch-ua': '"Google Chrome";v="112", "Chromium";v="112", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}

ProductData : TypeAlias = Dict[str, Any]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)



TOKEN = os.environ.get('SUPERDRUG_SCRAPER_TOKEN')
OWNER_ID = -1 # change this to preferred discord id

if not TOKEN:
    raise ValueError("No bot token provided!")


def search_sas(title : str) -> str:
    """Takes a given title and returns a URL to the SAS lookup page
    
    Args:
        title (str): Product title
    
    Returns:
        str: URL to SAS lookup
    """
    return f"https://sas.selleramp.com/sas/lookup?SasLookup%5Bsearch_term%5D={title.replace(' ', '+')}"

def build_info_embed(product_json: ProductData , code: int) -> discord.Embed:
    """Produces readable embed from product data with key info/links
    
    Args:
        product_json (ProductData): Product JSON data scraped from API
        code (int): Product code
    
    Returns:
        discord.Embed: Embed with key info/links
    """
    base_options = product_json['baseOptions'][0]['options'][0]
    price = base_options['priceData']['value']
    stock_level = base_options['stock']['stockLevel']
    url = f"https://superdrug.com/~/p/{code}"
    image_url = product_json['images'][0]['url']
    title = product_json['name']
    purchasable = product_json['purchasable']
    
    embed = discord.Embed(title=title, url=url, colour=0xFF69B4)
    # Two prices are shown, the first is original price, the second is the price with student discount
    embed.add_field(name="Price (SD)", value=f"£{price} - (£{round(float(price) * 0.9, 2)})", inline=True)
    embed.add_field(name="Stock", value=stock_level, inline=True)
    embed.add_field(name="Available Online", value=purchasable, inline=True)
    embed.add_field(name="SAS", value=f"[Click Me!]({search_sas(title)})", inline=True)
    embed.add_field(name="TCB", value=f"[Click Me!](https://www.topcashback.co.uk/superdrug)", inline=True)
    embed.add_field(name="Image URL", value=f"[Click Me!](https://media.superdrug.com{image_url})")
    embed.set_footer(text="Superdrug Scraper by jh33ls")
    
    return embed


async def fetch_data(code: int) -> tuple[ProductData, int]:
    """Returns product data from Superdrug API if successful, otherwise returns error message
    
    Args:
        code (int): Product code
    
    Returns:
        tuple[ProductData, int]: Product data, request status code
    """ 
    async with httpx.AsyncClient() as session:
            response = await session.get(
                f"https://api.superdrug.com/api/v2/sd/products/{code}"
                , timeout=30, headers=headers)
            data = response.json()
            return data, response.status_code

async def get_store_stock(code: int, loc: str) -> tuple[str, int]:
    """Returns stock level for a given store
    
    Args:
        code (int): Product code
        loc (str): Store location
        
    Returns:
        tuple[str, int]: Store location, stock level
    """
    url = f"https://api.superdrug.com/api/v2/sd/products/{code}/stock"
    query_params = {
        'location': loc,
        'country': 'GB',
        'fields': 'FULL',
        'pageSize': '5',
        'lang': 'en_GB',
        'curr': 'GBP'
    }
    async with httpx.AsyncClient(timeout=30, headers=headers) as session:
        response = await session.get(url, params=query_params)
        data = response.json()
        for store in data['stores']:
            if store['displayName'] == loc:
                return loc, store['stockInfo']['stockLevel']

@client.event
async def on_ready():
    """Called when the bot is ready to start working."""
    print(f"Logged in as {client.user}")

@tree.command(name='sync', description="Re-syncs all commands.")
async def sync(interaction: discord.Interaction):
    """Re-syncs all commands. Only the bot owner can use this command.
    
    Args:
        interaction (discord.Interaction): Discord interaction object    
    """
    if interaction.user.id == OWNER_ID:
        await tree.sync()
        await interaction.response.send_message("Synced!", ephemeral=True)
    else:
        await interaction.response.send_message("You are not allowed to use this command!")

                        
@tree.command(name='info', description='Scrape info for a product')
async def info(interaction: discord.Interaction, code: int):
    """Scrapes info for a product and returns an embed with key info/links
    
    Args:
        interaction (discord.Interaction): Discord interaction object
        code (int): Product code
    
    Returns:
        None: Sends an embed with key info/links to guild channel
    """
    if len(str(code)) == 6:
        try:
            data, status_code = await fetch_data(code)
            if status_code == 200:
                embed = build_info_embed(data, code)
            else:
                embed = discord.Embed(title="Error", colour=0xFF69B4)
                embed.add_field(name="Reason", value=data['errors'][0]['message'])                      
            await interaction.response.send_message(embed=embed)
        except  httpx.HTTPStatusError:
            await interaction.response.send_message(f"An error has occurred sending the request!")
    else:
        await interaction.response.send_message(f"Invalid code!")
        

@tree.command(name='storestockcheck', description='Checks stock for a product in nearby stores for a given location')
async def store_stock_check(interaction: discord.Interaction, code:int, location:str) -> None:
    """ Checks stock for a product in nearby stores for a given location
    
    Args:
        interaction (discord.Interaction): Discord interaction object
        code (int): Product code
        location (str): Location to check stock for
        
    Returns:
        None: Sends an embed with instock locations (max 20) to guild channel
    
    """
    
    if len(str(code)) != 6:
        await interaction.response.send_message(f"Invalid code! - Must be 6 digits long")
        return

    try:
        data, status_code = await fetch_data(code)
        await interaction.response.defer() # Defer response to prevent timeout
        if status_code == 200:
            async with httpx.AsyncClient(timeout=30, headers=headers) as session:
                query_params = {
                    "query": location,
                    "country": "GB",
                    "radius": "10000",
                    "fields": "FULL",
                    "pageSize": "20",
                    "lang": "en_GB",
                    "curr": "GBP"
                }
                store_response = await session.get( # Get nearby stores
                    "https://api.superdrug.com/api/v2/sd/stores"
                    , params=query_params)
                
                store_data_list = store_response.json()['stores']
            
            store_name_list = [store['displayName'] for store in store_data_list]
            
            if not store_name_list:
                await interaction.followup.send(f"No stores found!")
                return 

            tasks = [asyncio.create_task(get_store_stock(code, store)) for store in store_name_list]
            
            completed_tasks = await asyncio.gather(*tasks)
            # Filter out stores with no stock
            store_stock = {x[0]: x[1] for x in completed_tasks if x is not None and x[1] != 0}
            
            if not store_stock:
                await interaction.followup.send(f"No stores with stock found!")
                return
            
            title = data['name']
            embed = discord.Embed(title=title, colour=0xFF69B4, url=f"https://superdrug.com/~/p/{code}", description=f"_Returns only stores with stock_")
            embed_stock = '\n'.join([f"{x} : {store_stock[x]}" for x in store_stock]) + f"\n**Total Stock : {sum(store_stock.values())}**"
            embed.add_field(name='Store Stock', value=embed_stock, inline=True)
            embed.add_field(name="Notes", value=f"`Price : £{data['baseOptions'][0]['options'][0]['priceData']['value']}`", inline=False)
            embed.add_field(name="More Info", value=f"[API](https://api.superdrug.com/api/v2/sd/products/{code}) - [SAS]({search_sas(title)})", inline=False)
            embed.set_footer(text="Superdrug Scraper by jh33ls")
            
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(title="Error", colour=0xFF69B4)
            embed.add_field(name="Reason", value=data['errors'][0]['message'])
            await interaction.followup.send(embed=embed)
    except httpx.HTTPStatusError:
        await interaction.response.send_message(f"Could not get successful response from API!")
    except httpx.RequestError:
        await interaction.response.send_message(f"An error has occurred sending the request!")

if __name__ == "__main__":
    client.run(TOKEN)