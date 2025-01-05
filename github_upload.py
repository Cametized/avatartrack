import discord
from discord import app_commands
import requests

ROBLOX_API_BASE_URL = "https://users.roblox.com/v1"
THUMBNAIL_API_BASE_URL = "https://thumbnails.roblox.com/v1"
GAMES_API_BASE_URL = "https://games.roblox.com/v1"

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Command tree synchronized.")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}!")

def fetch_user_stats(user_id):
    """
    Fetch basic stats, headshot, full-body avatar images, and avatar change URLs for a user.
    """
    try:
        user_response = requests.get(f"{ROBLOX_API_BASE_URL}/users/{user_id}")
        user_response.raise_for_status()
        user_data = user_response.json()

        headshot_response = requests.get(
            f"{THUMBNAIL_API_BASE_URL}/users/avatar-headshot",
            params={"userIds": user_id, "size": "420x420", "format": "Png", "isCircular": False}
        )
        headshot_response.raise_for_status()
        headshot_data = headshot_response.json()
        headshot_url = headshot_data["data"][0]["imageUrl"] if headshot_data.get("data") else None

        full_body_response = requests.get(
            f"{THUMBNAIL_API_BASE_URL}/users/avatar",
            params={"userIds": user_id, "size": "720x720", "format": "Png", "isCircular": False}
        )
        full_body_response.raise_for_status()
        full_body_data = full_body_response.json()
        full_body_url = full_body_data["data"][0]["imageUrl"] if full_body_data.get("data") else None

        old_avatar_url = f"https://www.roblox.com/users/{user_id}/profile"
        new_avatar_url = f"https://www.roblox.com/users/{user_id}/avatar"

        return {
            "id": user_data["id"],
            "name": user_data["name"],
            "display_name": user_data["displayName"],
            "created": user_data["created"],
            "headshot_url": headshot_url,
            "full_body_url": full_body_url,
            "old_avatar_url": old_avatar_url,
            "new_avatar_url": new_avatar_url
        }
    except requests.RequestException as e:
        return {"error": str(e)}

def fetch_game_stats(game_id):
    """
    Fetch game stats and thumbnail for a game by its universe ID.
    """
    try:
        game_response = requests.get(f"{GAMES_API_BASE_URL}/games", params={"universeIds": game_id})
        game_response.raise_for_status()
        game_data = game_response.json()

        if not game_data.get("data"):
            return None

        game = game_data["data"][0]

        thumbnail_response = requests.get(
            f"{THUMBNAIL_API_BASE_URL}/games/icons",
            params={"universeIds": game_id, "size": "512x512", "format": "Png"}
        )
        thumbnail_response.raise_for_status()
        thumbnail_data = thumbnail_response.json()

        icon_url = thumbnail_data["data"][0]["imageUrl"] if thumbnail_data.get("data") else None

        return {
            "name": game["name"],
            "description": game.get("description", "No description available."),
            "active_players": game["playing"],
            "total_visits": game["visits"],
            "likes": game["upVotes"],
            "dislikes": game["downVotes"],
            "favorites": game.get("favoritedCount", "N/A"),
            "creator": game.get("creator", {}).get("name", "Unknown"),
            "icon_url": icon_url
        }
    except requests.RequestException as e:
        return {"error": str(e)}

@bot.tree.command(name="user_lookup", description="Look up stats for a Roblox account.")
@app_commands.describe(account_id="Enter the Roblox account ID")
async def user_lookup(interaction: discord.Interaction, account_id: str):
    """
    Slash command to look up a Roblox account by its ID and display stats in an embed.
    """
    await interaction.response.defer()

    user_stats = fetch_user_stats(account_id)
    if user_stats is None or "error" in user_stats:
        await interaction.followup.send(f"Error: Could not locate user with account ID '{account_id}'.")
        return

    embed = discord.Embed(title="Roblox User Stats", color=discord.Color.red())
    embed.set_image(url=user_stats["headshot_url"])  
    embed.add_field(name="Display Name", value=user_stats["display_name"], inline=False)
    embed.add_field(name="Username", value=user_stats["name"], inline=False)
    embed.add_field(name="User ID", value=user_stats["id"], inline=False)
    embed.add_field(name="Account Created", value=user_stats["created"], inline=False)
    embed.add_field(name="Old Avatar", value=f"[View Old Avatar]({user_stats['old_avatar_url']})", inline=True)
    embed.add_field(name="New Avatar", value=f"[View New Avatar]({user_stats['new_avatar_url']})", inline=True)
    embed.set_thumbnail(url=user_stats["full_body_url"])  
    embed.set_footer(text="View more on GitHub", icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
    embed.url = "https://github.com/Caminst"

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="game_lookup", description="Look up stats for a Roblox game.")
@app_commands.describe(game_id="Enter the Roblox game universe ID")
async def game_lookup(interaction: discord.Interaction, game_id: str):
    """
    Slash command to look up a Roblox game by its universe ID and display stats in an embed.
    """
    await interaction.response.defer()

    game_stats = fetch_game_stats(game_id)
    if game_stats is None or "error" in game_stats:
        await interaction.followup.send(f"Error: Could not fetch game stats for ID '{game_id}'.")
        return

    embed = discord.Embed(title="Roblox Game Stats", description=game_stats["description"], color=discord.Color.red())
    embed.set_thumbnail(url=game_stats["icon_url"])
    embed.add_field(name="Game Name", value=game_stats["name"], inline=False)
    embed.add_field(name="Creator", value=game_stats["creator"], inline=False)
    embed.add_field(name="Active Players", value=game_stats["active_players"], inline=False)
    embed.add_field(name="Total Visits", value=game_stats["total_visits"], inline=False)
    embed.add_field(name="Likes", value=game_stats["likes"], inline=False)
    embed.add_field(name="Dislikes", value=game_stats["dislikes"], inline=False)
    embed.add_field(name="Favorites", value=game_stats["favorites"], inline=False)
    embed.set_footer(text="View more on GitHub", icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
    embed.url = "https://github.com/Caminst"

    await interaction.followup.send(embed=embed)

if __name__ == "__main__":
    bot.run("help")
