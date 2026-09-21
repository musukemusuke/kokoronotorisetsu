# main.py - ボットのエントリーポイント
import discord
import os
from discord.ext import commands
from discord import app_commands

# Discordボットのインテントを設定
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Botオブジェクトを作成（cogを使うためにcommands.Botを使用）
bot = commands.Bot(command_prefix="!", intents=intents)

# 起動時にコマンドをDiscordに同期する
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('------')
    # Cogをロード
    await bot.load_extension("cogs.manuals")
    # スラッシュコマンドをDiscordサーバーに同期（bot.treeを使用）
    await bot.tree.sync()
    print("スラッシュコマンドを同期しました。")

# ボットを実行
if __name__ == "__main__":
    try:
        bot.run(os.environ['BOT_TOKEN'])
    except KeyError:
        print("環境変数 'BOT_TOKEN' が設定されていません。")
        print("Discord Developer Portalで取得したボットのトークンを環境変数に設定してください。")
    except discord.LoginFailure:
        print("ボットのトークンが無効です。正しいトークンが設定されているか確認してください。")