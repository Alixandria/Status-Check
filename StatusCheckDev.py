import json
import os
import disnake
from disnake.ext import commands

bot = commands.Bot(
    test_guilds=[356517560855953410], intents=disnake.Intents.all()

)

ALLOWED_STATUSES = ["Available", "Unavailable", "Slow to Respond", "Mobile Only", "On Break"]
USER_STATUSES = {}
TOKEN = os.getenv("BOT_TOKEN")


@bot.slash_command(description="Set your status!")
async def status(
        inter: disnake.AppCommandInteraction, new_status: str = commands.Param(choices=ALLOWED_STATUSES)):
    USER_STATUSES[inter.author.id] = new_status
    with open("statuses.json", "w") as f:
        json.dump(USER_STATUSES, f)
    await inter.response.send_message(f"You have set your status to {new_status}", ephemeral=True)


@bot.slash_command(description="Get statuses")
async def statuses(inter: disnake.AppCommandInteraction):
    embed = disnake.Embed(
        title="Current Staff Availability",
        description="The following staff members have reported statuses on the server.",
        color=0xFD9C9C
    )

    for user_id, cur_status in USER_STATUSES.items():
        user = inter.guild.get_member(user_id)
        embed.add_field(name=user.display_name, value=cur_status)

    await inter.response.send_message(embed=embed)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.slash_command(description="say hi")
async def helloworld(inter: disnake.AppCommandInteraction):
    caller = inter.author.mention
    highest_role = inter.author.top_role.mention

    await inter.response.send_message(
        f"{caller}, I am responding to commands, you appear to be {highest_role} on Staff!",
        allowed_mentions=None, ephemeral=True)


def loadstatuses():
    try:
        with open("statuses.json") as f:
            statuses = json.load(f)
    except FileNotFoundError:
        return
    USER_STATUSES.update({int(k): v for k, v in statuses.items()})


if __name__ == "__main__":
    loadstatuses()
    bot.run(TOKEN)
