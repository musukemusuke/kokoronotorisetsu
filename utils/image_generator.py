from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def create_manual_image(username: str, content: str) -> BytesIO:
    # 画像の基本設定（横幅800px、高さは内容に合わせて自動調整）
    bg_color = (240, 248, 255)  # 薄い青背景
    text_color = (20, 20, 40)   # 濃い文字色
    title_color = (30, 60, 120) # タイトルの色
    
    # フォント読み込み
    try:
        font_path = "fonts/NotoSansJP-Regular.ttf"
        title_font = ImageFont.truetype(font_path, 36)
        content_font = ImageFont.truetype(font_path, 20)
        header_font = ImageFont.truetype(font_path, 24) # ヘッダー用フォントもここで定義
    except IOError:
        print(f"Warning: Font file not found at {font_path}. Using default font.")
        title_font = ImageFont.load_default(size=36)
        content_font = ImageFont.load_default(size=20)
        header_font = ImageFont.load_default(size=24)
    
    # テキストを改行して描画可能な行数を計算
    content_lines = []
    for line in content.split('\n'):
        # 1行が長すぎる場合は折り返す
        current_line = ""
        for char in line:
            test_line = current_line + char
            bbox = content_font.getbbox(test_line)
            if bbox[2] > 720:  # 横幅720pxを超えたら折り返し
                content_lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            content_lines.append(current_line)
    
    # 必要な画像の高さを計算
    line_height = 30
    title_height = 80
    padding = 50
    total_height = title_height + (len(content_lines) * line_height) + padding * 2
    
    # 画像を作成
    img = Image.new('RGB', (800, total_height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # タイトルを描画
    draw.text((40, 40), f"{username}の取扱説明書", fill=title_color, font=title_font)
    
    # 内容を描画（見出し行は少し太く/大きく表示）
    y = 120
    for line in content_lines:
        # 【で始まる行は見出しとして少し大きく描画
        if line.startswith("【"):
            draw.text((40, y), line, fill=title_color, font=header_font)
        else:
            draw.text((40, y), line, fill=text_color, font=content_font)
        y += line_height
    
    # 画像をBytesIOに保存して返す
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer