import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, Any
from utils.image_generator import create_manual_image
from utils.data_manager import load_manuals, save_manuals

# モーダル（ポップアップ入力フォーム）の定義
class ManualModal(discord.ui.Modal, title="取扱説明書を作成する"):
    birthday = discord.ui.TextInput(
        label="誕生日（任意）",
        style=discord.TextStyle.short,
        placeholder="例: 1995/05/20",
        required=False
    )
    favorite = discord.ui.TextInput(
        label="好きなもの（任意）",
        style=discord.TextStyle.short,
        placeholder="例: ラーメン、ゲーム",
        required=False
    )
    dislike = discord.ui.TextInput(
        label="苦手なこと（任意）",
        style=discord.TextStyle.short,
        placeholder="例: 大勢の前で話すこと",
        required=False
    )
    manual_content = discord.ui.TextInput(
        label="自由記述欄（その他伝えたいこと）",
        style=discord.TextStyle.long,
        placeholder="その他伝えたいことを何でも書いてください。",
        required=True,
        max_length=4000,
        min_length=1
    )

    def __init__(self, manuals: Dict[str, Any], user_id: str = None):
        super().__init__()
        self.manuals = manuals
        # 編集時に既存の内容をプリセット
        if user_id and user_id in manuals:
            content = manuals[user_id]["content"]
            if "【誕生日】" in content:
                birthday = content.split("【誕生日】\n")[1].split("\n【")[0]
                self.birthday.default = birthday
            if "【好きなもの】" in content:
                favorite = content.split("【好きなもの】\n")[1].split("\n【")[0]
                self.favorite.default = favorite
            if "【苦手なこと】" in content:
                dislike = content.split("【苦手なこと】\n")[1].split("\n【")[0]
                self.dislike.default = dislike
            if "【自由記述】" in content:
                manual_content = content.split("【自由記述】\n")[1]
                self.manual_content.default = manual_content

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        # テンプレート項目と自由記述をまとめて保存
        full_content = []
        if self.birthday.value:
            full_content.append(f"【誕生日】\n{self.birthday.value}")
        if self.favorite.value:
            full_content.append(f"\n【好きなもの】\n{self.favorite.value}")
        if self.dislike.value:
            full_content.append(f"\n【苦手なこと】\n{self.dislike.value}")
        full_content.append(f"\n【自由記述】\n{self.manual_content.value}")
        
        self.manuals[user_id] = {
            "content": "\n".join(full_content),
            "empathies": []
        }
        save_manuals(self.manuals)
        await interaction.response.send_message("取扱説明書を保存しました！いつでも他のユーザーに見てもらえます。", ephemeral=True)

# 共感ボタンのViewクラス
class EmpathyButton(discord.ui.View):
    def __init__(self, target_id: str, manuals: Dict[str, Any]):
        super().__init__(timeout=None)
        self.target_id = target_id
        self.manuals = manuals

    @discord.ui.button(label="共感した！", style=discord.ButtonStyle.primary, emoji="💙")
    async def empathy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.target_id in self.manuals:
            # 同じユーザーが複数回共感できないように制御
            if interaction.user.id in self.manuals[self.target_id]["empathies"]:
                await interaction.response.send_message("すでにこのユーザーに共感しています！", ephemeral=True)
                return
            # 共感を追加して保存
            self.manuals[self.target_id]["empathies"].append(interaction.user.id)
            save_manuals(self.manuals)
            # ボタンのラベルを更新
            count = len(self.manuals[self.target_id]["empathies"])
            button.label = f"共感した！ ({count})"
            await interaction.response.send_message(f"このユーザーに共感しました！", ephemeral=True)
            await interaction.message.edit(view=self)
        else:
            await interaction.response.send_message("エラーが発生しました。", ephemeral=True)

# 取扱説明書関連のコマンドをまとめたCog
class ManualsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manuals = load_manuals()

    # /create_manual - 自分の取扱説明書を作成するモーダルを開く
    @app_commands.command(name="create_manual", description="自分の「取扱説明書」を作成します")
    async def create_manual(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ManualModal(self.manuals))

    # /edit_manual - 自分の取扱説明書を編集する
    @app_commands.command(name="edit_manual", description="自分の「取扱説明書」を編集します")
    async def edit_manual(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        await interaction.response.send_modal(ManualModal(self.manuals, user_id))

    # /view_manual - 指定したユーザーの取扱説明書を閲覧します
    @app_commands.command(name="view_manual", description="指定したユーザーの「取扱説明書」を閲覧します")
    async def view_manual(self, interaction: discord.Interaction, target: discord.User):
        target_id = str(target.id)
        if target_id in self.manuals and self.manuals[target_id]["content"] != "":
            content = self.manuals[target_id]["content"]
            # 画像を生成
            image_buffer = create_manual_image(target.display_name, content)
            file = discord.File(image_buffer, filename=f"{target.id}_manual.png")
            # 共感数を取得
            empathy_count = len(self.manuals[target_id].get("empathies", []))
            # テキストEmbedと画像を両方送信
            embed = discord.Embed(
                title=f"{target.display_name}の「取扱説明書」",
                description=f"画像として生成しました！\n現在の共感数: {empathy_count}",
                color=discord.Color.blue()
            )
            # 共感ボタンを追加して送信
            view = EmpathyButton(target_id, self.manuals)
            if empathy_count > 0:
                view.children[0].label = f"共感した！ ({empathy_count})"
            await interaction.response.send_message(embed=embed, file=file, view=view, ephemeral=True)
        else:
            await interaction.response.send_message(f"{target.display_name}さんはまだ取扱説明書を作成していません。", ephemeral=True)

    # /delete_manual - 自分の取扱説明書を削除します
    @app_commands.command(name="delete_manual", description="自分の「取扱説明書」を削除します")
    async def delete_manual(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id in self.manuals:
            del self.manuals[user_id]
            save_manuals(self.manuals)
            await interaction.response.send_message("あなたの「取扱説明書」を削除しました。", ephemeral=True)
        else:
            await interaction.response.send_message("あなたはまだ「取扱説明書」を作成していません。", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ManualsCog(bot))