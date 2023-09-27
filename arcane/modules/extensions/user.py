from datetime import datetime
from random import choice

import pytz
from dateutil.relativedelta import relativedelta

from arcane.bot import bot
from arcane.modules.twitchapi import get_user_creation, get_stream_started_at, get_followers


@bot.command(name='8ball', aliases=['8b'])
async def cmd_eight_ball(msg, question: str = None) -> None:
    if question:
        eight_ball_responses = (
            'It is certain.',
            'It is decidedly so.',
            'Without a doubt.',
            'Yes, definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            'Reply hazy, try again.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Concentrate and ask again.',
            'Don\'t count on it.',
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.'
        )
        await msg.reply(choice(eight_ball_responses))
    else:
        await msg.reply('Please ask a question')


@bot.command(name='accountage', aliases=['age'])
async def cmd_accountage(msg) -> None:
    channel_name = msg.author
    user_created_at = await get_user_creation(channel_name)

    if user_created_at:
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        age_delta = relativedelta(now, user_created_at)

        years = age_delta.years
        months = age_delta.months
        days = age_delta.days
        hours = age_delta.hours
        minutes = age_delta.minutes

        age_text = []

        if years > 0:
            age_text.append(f'{years}y')
        if months > 0:
            age_text.append(f'{months}m')
        if days > 0:
            age_text.append(f'{days}d')
        if hours > 0:
            age_text.append(f'{hours}h')
        if minutes > 0:
            age_text.append(f'{minutes}m')

        age_str = ' '.join(age_text)
        await msg.reply(age_str)
    else:
        return


@bot.command(name='uptime')
async def cmd_uptime(msg) -> None:
    channel_name = msg.channel
    stream_started_at = await get_stream_started_at(channel_name)

    if stream_started_at:
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)

        uptime_delta = now - stream_started_at
        days = uptime_delta.days
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds // 60) % 60

        uptime_text = ''
        if days > 0:
            uptime_text += f'{days}d '
        if hours > 0:
            uptime_text += f'{hours}h '
        uptime_text += f'{minutes}m'

        await msg.reply(uptime_text)
    else:
        await msg.reply('Offline')


@bot.command(name='followsince')
async def cmd_followsince(msg) -> None:
    target_user = msg.author
    channel_name = msg.channel

    follower_data = await get_followers(channel_name)
    follower = next((follower for follower in follower_data if follower['user_login'] == target_user), None)

    if follower:
        follow_date = datetime.strptime(follower['followed_at'], '%Y-%m-%dT%H:%M:%SZ')
        now = datetime.utcnow()

        time_since_follow = now - follow_date
        days = time_since_follow.days
        follow_since_text = follow_date.strftime('%d %B %Y')

        if days == 1:
            days_text = '1 day'
        else:
            days_text = f'{days} days'

        await msg.reply(f'{follow_since_text} ({days_text})')
    elif target_user == channel_name:
        await msg.reply(f'Your broadcaster 🎙️')
    else:
        await msg.reply(f'You\'re not followed to the channel!')


@bot.command(name='followage')
async def cmd_followage(msg) -> None:
    target_user = msg.author
    channel_name = msg.channel

    follower_data = await get_followers(channel_name)
    follower = next((follower for follower in follower_data if follower['user_login'] == target_user), None)

    if follower:
        follow_date = datetime.strptime(follower['followed_at'], '%Y-%m-%dT%H:%M:%SZ')
        now = datetime.utcnow()

        time_since_follow = relativedelta(now, follow_date)

        followage_text = ''
        if time_since_follow.years > 0:
            followage_text += f'{time_since_follow.years}y '
        if time_since_follow.months > 0:
            followage_text += f'{time_since_follow.months}mo '
        if time_since_follow.days > 0:
            followage_text += f'{time_since_follow.days}d'

        await msg.reply(followage_text)
    elif target_user == channel_name:
        await msg.reply(f'Your broadcaster 🎙️')
    else:
        await msg.reply(f'You\'re not followed to the channel!')
