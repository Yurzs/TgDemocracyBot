import base64
import logging
import os
import random
import re

import asyncpg
from aiogram import Bot, types, Dispatcher, executor, utils
from sqlalchemy import and_

import config
import models

API_TOKEN = os.environ.get('BOT_TOKEN')
logging.basicConfig(level=logging.CRITICAL)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def invite_user(chat_id, user):
    """
    TBD
    :param chat_id:
    :param user:
    :return:
    """
    pass


async def kick_user():
    """
    TBD
    :return:
    """
    pass


async def mute_user():
    """
    TBD
    :return:
    """
    pass


async def delete_spam():
    """
    TBD
    :return:
    """
    pass


@dp.message_handler(commands='invite')
async def invite_new_user_to_chat(message: types.Message):
    """
    Creates new poll for new possible chat user
    :param message:
    :return:
    """
    if message.entities:
        try:
            for mention in [entity for entity in message.entities if entity.type == 'mention']:
                poll = await models.Poll.create(chat_id=message.chat.id, text_id=1)
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                yes = types.InlineKeyboardButton(text='👍', callback_data=f'poll_{poll.id}_1')
                no = types.InlineKeyboardButton(text='👎', callback_data=f'poll_{poll.id}_2')
                keyboard.add(yes, no)
                text = await models.LangText.query.where(models.LangText.id == 1).gino.first()

                sent_message = await message.reply(text=text.text.format(
                    inviter=f'@{message.from_user.username if message.from_user.username else message.from_user.full_name}',
                    invitee=message.text[mention.offset: mention.offset + mention.length]),
                    reply_markup=keyboard)
                await bot.pin_chat_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
                return
                # await invite_user(message.chat.id, user.)
            else:
                await message.reply('Please send me users username in format /invite @username')
        except asyncpg.exceptions.UniqueViolationError:
            await message.reply('Poll already exist')


@dp.message_handler(lambda message: re.match('/start [0-9A-z=]+', message.text))
async def start_message(message: types.Message):
    """
    Deep linking for joining chat
    :param message:
    :return:
    """
    invite_link = await models.InviteLink.query.where(
        models.InviteLink.internal_link == message.text.split(' ')[1].replace('=', '')).gino.first()
    if invite_link:
        if message.from_user.username.lower() == invite_link.username.replace('@', '').lower():
            try:
                user_invite = await bot.export_chat_invite_link(chat_id=invite_link.chat_id)
            except utils.exceptions.BadRequest as error:
                await message.reply(text=error)
                return
            await message.reply(text=user_invite)
        else:
            await message.reply(text='Link is not yours!')
    else:
        await message.reply('Unknown link')


@dp.message_handler(commands='start')
async def start_message(message: types.Message):
    """
    Start message. Bots frontpage
    TBD
    :param message:
    :return:
    """

    welcome = """Welcome to DemocracyBot!
Currently availiable functions are 
/invite @username"""
    await message.reply(welcome)
    print(message.to_python())


@dp.callback_query_handler(lambda callback: re.match('poll_[0-9]+_[0-9]', callback.data))
async def save_vote(callback: types.CallbackQuery):
    """
    Callback for votes. If > 50 votes triggers ability to join chat via deeplink to bot
    :param callback:
    :return:
    """
    try:
        vote = await models.Vote.create(poll_id=int(callback.data.split('_')[1]), user_id=callback.from_user.id,
                                        result=int(callback.data.split('_')[2]))
    except asyncpg.exceptions.UniqueViolationError:
        if not int(callback.data.split('_')[2]) == (
                await models.Vote.query.where(and_(models.Vote.poll_id == int(callback.data.split('_')[1]),
                                                   models.Vote.user_id == callback.from_user.id)).gino.first()).result:
            status, vote = await models.Vote.update.values(result=int(callback.data.split('_')[2])).where(
                and_(models.Vote.poll_id == int(callback.data.split('_')[1]),
                     models.Vote.user_id == callback.from_user.id)).gino.status()
        else:
            await models.Vote.delete.where(and_(models.Vote.poll_id == int(callback.data.split('_')[1]),
                                                models.Vote.user_id == callback.from_user.id)).gino.status()
    yes_votes = len(await models.Vote.query.where(
        and_(models.Vote.poll_id == int(callback.data.split('_')[1]), models.Vote.result == 1)).gino.all())
    no_votes = len(await models.Vote.query.where(
        and_(models.Vote.poll_id == int(callback.data.split('_')[1]), models.Vote.result == 2)).gino.all())
    users_in_group = await bot.get_chat_members_count(callback.message.chat.id)
    if yes_votes >= int(users_in_group) / 2:
        invlink = base64.urlsafe_b64encode(
            int.to_bytes(random.randrange(100000, 99999999999), length=10, byteorder='big')). \
            decode()
        text = await models.LangText.query.where(
            and_(models.LangText.name == 'Invite_YES', models.LangText.language_id == (
                await models.Language.query.where(models.Language.name == 'Russian').gino.first()).id)).gino.first()
        invitee = callback.message.text[
                  callback.message.entities[1].offset:callback.message.entities[1].length + callback.message.entities[
                      1].offset]
        invite_link = f't.me/{(await bot.get_me()).username}?start={invlink.replace("=", "")}'
        try:
            await models.InviteLink.create(chat_id=callback.message.chat.id, internal_link=invlink.replace('=', ''),
                                           username=invitee)
        except asyncpg.exceptions.UniqueViolationError:
            await models.InviteLink.update.values(internal_link=invlink.replace("=", "")).where(
                and_(models.InviteLink.chat_id == callback.message.chat.id,
                     models.InviteLink.username == invitee)).gino.status()
        sent_message = await bot.edit_message_text(text=text.text.format(invitee=invitee,
                                                                         botlink=invite_link),
                                                   chat_id=callback.message.chat.id,
                                                   message_id=callback.message.message_id)

        await bot.pin_chat_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
        await models.Vote.delete.where(models.Vote.poll_id == int(callback.data.split('_')[1])).gino.status()
        await models.Poll.delete.where(models.Poll.id == int(callback.data.split('_')[1])).gino.status()
        return
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    yes = types.InlineKeyboardButton(text=f'{yes_votes} 👍', callback_data=f'poll_{callback.data.split("_")[1]}_1')
    no = types.InlineKeyboardButton(text=f'{no_votes} 👎', callback_data=f'poll_{callback.data.split("_")[1]}_2')
    keyboard.add(yes, no)

    await bot.edit_message_text(text=callback.message.text, reply_markup=keyboard,
                                message_id=callback.message.message_id,
                                chat_id=callback.message.chat.id)
    return


@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def new_chat_members(message: types.Message):
    """
    Check chat joining users for link revocation after 1st joining
    :param message:
    :return:
    """
    for user in message.new_chat_members:
        invite_link = await models.InviteLink.query.where(and_(models.InviteLink.chat_id == message.chat.id,
                                                               models.InviteLink.username == f'{user.username.lower()}')).gino.first()
        if invite_link:
            # print(await models.InviteLink.delete.where(models.InviteLink.id == invite_link.id).gino.status())
            print(await bot.export_chat_invite_link(chat_id=message.chat.id))

    return


@dp.message_handler(commands='init_russian')
async def add(message: types.Message):
    """
    TBD Language packs
    :param message:
    :return:
    """
    language = await models.Language.create(name='Russian')
    text = await models.LangText.create(
        text="""{inviter} предлагает позвать в чат {invitee}. Вы согласны?
Он(а) сможет вступить в чат если наберется больше 50% голосов "за" из всех участников""",
        language_id=language.id,
        name='Invite')
    text = await models.LangText.create(text='{invitee} будет приглашен. Перешлите ему эту ссылку {botlink}',
                                        language_id=language.id,
                                        name='Invite_YES')
    text = await models.LangText.create(text='К сожалению {invitee} не будет приглашен',
                                        language_id=language.id,
                                        name='Invite_NO')


#     print(text.id)

if __name__ == '__main__':
    # config.loop.run_until_complete(config.db.gino.drop_all()) # You know what to do
    config.loop.run_until_complete(config.db.gino.create_all())
    executor.start_polling(dp, skip_updates=False, loop=config.loop)
