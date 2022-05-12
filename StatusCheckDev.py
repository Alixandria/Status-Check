import os
import sys
import datetime
import logging

import disnake
from disnake.ext import commands
from lib import BotConfig

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

bot = commands.Bot(
    test_guilds=[GUILD ID]
)

config = BotConfig.get_config()
status_db = BotConfig.get_config(name="statuses")

STATUSES = [
    "✅ Available",
    "❎ Unavailable",
    "🕰️ Slow to Respond",
    "📱 Mobile Only",
    " ✈ On Break",
]


### HELPER METHODS
async def update_wallboard():
    wallboard_conf = config.get('wallboard', {})

    if not wallboard_conf:
        # suppress if no wallboard defined yet
        return

    channel = bot.get_channel(wallboard_conf['channel_id'])
    message = await channel.fetch_message(wallboard_conf['message_id'])

    await message.edit(embed=generate_status_embed())
    logging.info("Issued Status Board update API call")


def generate_status_embed():
    embed = disnake.Embed(
        title="Staff Statuses Report",
        description="The following staff members have reported statuses on the server.",
        color=0xFFFF00,
        timestamp=datetime.datetime.now()
    )

    reverse_map = {}
    for user_id, cur_status in status_db.dump().items():
        reverse_map[cur_status] = reverse_map.get(cur_status, []) + [user_id]

    ordered_statuses = sorted(reverse_map, key=STATUSES.index)

    for status in ordered_statuses:
        embed.add_field(name=status, value=", ".join(f"<@{i}>" for i in reverse_map[status]), inline=False)

    return embed


### BOT METHODS
@bot.event
async def on_ready():
    logging.info("StatusCheck Bot is ready!")
    await update_wallboard()


@bot.slash_command(description="Create a Status Board to track statuses for users")
async def wallboard(inter: disnake.AppCommandInteraction):
    wallboard_config = config.get('wallboard', {})

    if wallboard_config:
        await inter.response.send_message(
            "A Status Board is already configured! Please delete the old wallboard from the "
            "config first.", ephemeral=True)
        logging.warning("Attempted to create a Status Board when one already exists. Aborting.")
        return

    status_view = disnake.ui.View(timeout=None)
    status_view.add_item(disnake.ui.Select(
        custom_id="status:select",
        placeholder="Select your new status...",
        options=[disnake.SelectOption(label=la) for la in STATUSES]
    ))

    message: disnake.Message = await inter.channel.send(embed=generate_status_embed(), view=status_view)
    wallboard_config = {"channel_id": message.channel.id, "message_id": message.id}
    config.set('wallboard', wallboard_config)

    logging.info(f"New wallboard created in #{message.channel.name}, message ID {message.id}")
    await inter.response.send_message("A new Status Board was created and saved!", ephemeral=True)


@bot.slash_command(name="status", description="Set the status for yourself")
async def set_status(inter: disnake.AppCommandInteraction, status: str = commands.Param(choices=STATUSES)):
    status_db.set(str(inter.author.id), status)
    logging.info(f"User {inter.author} has set their status to {status} via slash command")
    await update_wallboard()
    await inter.response.send_message(f"Your status has been set to {status}.", ephemeral=True)


@bot.slash_command(description="Administration Commands")
async def statusadm(inter: disnake.AppCommandInteraction):
    pass


@statusadm.sub_command(name="set", description="Change a user's status")
async def force_set_status(inter: disnake.AppCommandInteraction, user: disnake.Member,
                           status: str = commands.Param(choices=STATUSES)):
    status_db.set(str(user.id), status)
    logging.info(f"User {user} has had status changed to {status}")
    await update_wallboard()
    await inter.response.send_message(f"The status for {user.mention} has been set to {status}.", ephemeral=True)


@statusadm.sub_command(name="clear", description="Remove a status from a user")
async def force_remove_status(inter: disnake.AppCommandInteraction, user: disnake.Member):
    status_db.delete(str(user.id))
    logging.info(f"User {user} has had status forcefully cleared")
    await update_wallboard()
    await inter.response.send_message(f"{user.mention} has been removed from the Status Board.", ephemeral=True)


@bot.event
async def on_message_interaction(interaction: disnake.MessageInteraction):
    custom_id = interaction.data.custom_id

    if custom_id == "status:select":
        new_status = interaction.data.values[0]
        status_db.set(str(interaction.author.id), new_status)
        logging.info(f"{interaction.author} has set their status to {new_status} via Status Board dropdown")

        await interaction.response.edit_message(embed=generate_status_embed())
    else:
        logging.warning(f"Got unknown interaction with ID: {custom_id}")


if __name__ == "__main__":
    bot.run(os.environ['BOT_TOKEN'])

## Huge thank you to all of those that have helped me along the way
