from haxbod import settings


def owner_only():
    def decorator(func):
        async def wrapper(self, ctx, *args, **kwargs):
            if str(ctx.author.id) == settings.OWNER_ID:
                await func(self, ctx, *args, **kwargs)
            else:
                await ctx.reply(f'Sorry, {ctx.author.name}, you do not have permission to use this command.')
        return wrapper
    return decorator
