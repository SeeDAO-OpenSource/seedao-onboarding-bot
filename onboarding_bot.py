##############
#
#
#
import os
import time

import requests
from discord.ext import commands
from dotenv import load_dotenv
from notion_client import Client, APIResponseError, APIErrorCode

load_dotenv()
# notion API link
base_url = "https://api.notion.com/v1/databases/"
# discord token > .env DISCORD_TOKEN
TOKEN = os.getenv('DISCORD_TOKEN')
# discord guild > .env DISCORD_GUILD
GUILD = os.getenv('DISCORD_GUILD')
# 链接notion API > .env NOTION_API
notion = Client(auth=os.getenv('NOTION_API'))
# 预设discord呼出命令为 ‘/’
bot = commands.Bot(command_prefix='/')


def check_new_entry():
    """
    自动检测新数据
    v0.1 - 目前只支持开发者工会DB
    NOTION_DB_ID为Notion table独有的id
    通过新增栏“审核”去筛选未审核人员
    :return:
    """
    notion_auth = Client(auth=os.getenv('NOTION_API'))
    try:
        my_page = notion_auth.databases.query(
            **{
                "database_id": os.getenv('NOTION_DB_ID'),
                "filter": {
                    "property": "Verify",
                    "checkbox": {
                        "equals": False,
                    },
                },
            }
        )
        return len(my_page), my_page['results'][0]['url']
    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            return error.code


@bot.command(name='register')
async def register(ctx):
    """
    机器人指令 ‘/register’
    通过机器人指令呼叫出google doc并进行注册
    注册时间间隔为5分钟
    5分钟之后返回discord webhook
    :param ctx:
    :return:
    """
    role_id = '979900234731778059'
    welcome_message = "欢迎来到开发者工会\n" \
                      "请填写这个表单来完成新人登入\n" \
                      "https://docs.google.com/forms/d/e/1FAIpQLScglerytpTdO1zSSn68cjrmNAP1Xotxts9C8YL3QZQo5hzbnQ/viewform"

    await ctx.send(welcome_message)

    time.sleep(300)

    dc_webhook()

def dc_webhook():
    """
    Discord webhook用于监控新成员，如果有新成员则通过webhook返回到discord中
    :return:
    """
    role_id = '979900234731778059'
    number_new_application, url = check_new_entry()
    if 0 < number_new_application:
        hook_message = "<@&{}>\n".format(role_id) + "新人报道! \n" + url
        data = {
            "content": hook_message.encode('utf-8'),
            "username": "Captain Hook"
        }
        requests.post(os.getenv('webhook_URL'), data=data)


bot.run(TOKEN)
