from haxbod import settings


def owner_only():
    def decorator(func):
        async def wrapper(self, ctx, *args, **kwargs):
            if ctx.author.id == settings.OWNER_ID:
                await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


def check_user_roles(ctx):
    user_roles = []
    if ctx.author.is_broadcaster: user_roles.append('broadcaster')
    if ctx.author.is_mod: user_roles.append('moderator')
    if ctx.author.is_subscriber: user_roles.append('subscriber')
    if ctx.author.is_turbo: user_roles.append('turbo')
    if ctx.author.is_vip: user_roles.append('vip')
    return user_roles


def permission(*allowed_roles):
    def decorator(func):
        async def wrapper(self, ctx, *args, **kwargs):
            for role in allowed_roles:
                if role in check_user_roles(ctx):
                    return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator
