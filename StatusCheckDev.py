import os
import disnake
from disnake.ext import commands

bot = commands.Bot(
    test_guilds=[356517560855953410]
)

ALLOWED_STATUSES = ["Available", "Unavailable", "Slow to Respond", "Mobile Only", "On Break"]
USER_STATUSES = {}

@bot.slash_command(description="Set your status!")
async def status(
    inter: disnake.AppCommandInteraction, new_status: str = commands.Param(choices=ALLOWED_STATUSES)):
    USER_STATUSES[inter.author] = new_status 
    await inter.response.send_message(f"You have set your status to {new_status}", ephemeral=True)

@bot.slash_command(description="Get statuses")
async def statuses(inter: disnake.AppCommandInteraction):
    embed = disnake.Embed(
        title="Current Staff Availability",
        description="The following staff members have reported statuses on the server.",
        color=0xFD9C9C
    )

    for user, cur_status in USER_STATUSES.items():
        embed.add_field(name=user.display_name, value=cur_status)

    await inter.response.send_message(embed=embed)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(description="say hi")
async def helloworld (inter: disnake.AppCommandInteraction):
    caller = inter.author.mention
    highest_role = inter.author.top_role.mention

    await inter.response.send_message(f"{caller}, I am responding to commands, you appear to be {highest_role} on Staff!", 
                                    allowed_mentions=None, ephemeral=True)

    

if __name__ == "__main__":
    bot.run("token")