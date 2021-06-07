import logging
from html import unescape
from urllib.parse import quote_plus

from discord import Embed, HTTPException
from discord.ext import commands

from bot import bot
from bot.constants import Colours, Emojis

logger = logging.getLogger(__name__)

BASE_URL = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&site=stackoverflow&q={query}"
SEARCH_URL = "https://stackoverflow.com/search?q={query}"
ERR_EMBED = Embed(
    title="Error in fetching results from Stackoverflow",
    description=(
        "Sorry, there was en error while trying to fetch data from the Stackoverflow website. Please try again in some "
        "time. If this issue persists, please contact the staff or send a message in #dev-contrib."
    ),
    color=Colours.soft_red
)


class Stackoverflow(commands.Cog):
    """Contains command to interact with stackoverflow from discord."""

    def __init__(self, bot: bot.Bot):
        self.bot = bot

    @commands.command(aliases=["so"])
    @commands.cooldown(1, 15, commands.cooldowns.BucketType.user)
    async def stackoverflow(self, ctx: commands.Context, *, search_query: str) -> None:
        """Sends the top 5 results of a search query from stackoverflow."""
        encoded_search_query = quote_plus(search_query)

        for _ in range(3):
            async with self.bot.http_session.get(BASE_URL.format(query=encoded_search_query)) as response:
                if response.status == 200:
                    data = await response.json()
                    break
                else:
                    logger.error(f'Status code is not 200, it is {response.status}')
                    continue
        if response.status != 200:  # If the status is still not 200 after the 3 tries
            await ctx.send(embed=ERR_EMBED)
            return
        elif not data['items']:
            no_search_result = Embed(
                title=f"No search results found for {search_query!r}",
                color=Colours.soft_red
            )
            await ctx.send(embed=no_search_result)
            return

        top5 = data["items"][:5]
        embed = Embed(
            title=f"Search results for {search_query!r} - Stackoverflow",
            url=SEARCH_URL.format(query=encoded_search_query),
            description=f"Here are the top {len(top5)} results:",
            color=Colours.orange
        )
        for item in top5:
            embed.add_field(
                name=unescape(item['title']),
                value=(
                    f"[{Emojis.reddit_upvote} {item['score']}    "
                    f"{Emojis.stackoverflow_views} {item['view_count']}     "
                    f"{Emojis.reddit_comments} {item['answer_count']}   "
                    f"{Emojis.stackoverflow_tag} {', '.join(item['tags'][:3])}]"
                    f"({item['link']})"
                ),
                inline=False)
        embed.set_footer(text="View the original link for more results.")
        try:
            await ctx.send(embed=embed)
        except HTTPException:
            search_query_too_long = Embed(
                title="Your search query is too long, please try shortening your search query",
                color=Colours.soft_red
            )
            await ctx.send(embed=search_query_too_long)


def setup(bot: bot.Bot) -> None:
    """Loads Stackoverflow Cog."""
    bot.add_cog(Stackoverflow(bot))

# Upvote and Comment icon taken from Reddit bot
# Tag icon made by Freepik (https://www.flaticon.com/authors/freepik) from www.flaticon.com, and edited by me
