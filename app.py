import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime
from google.colab import files
import io

# ステップ1: HTMLファイルをアップロード
uploaded = files.upload()
file_name = list(uploaded.keys())[0]
html = uploaded[file_name].decode('utf-8')

# ステップ2: HTMLのパース
soup = BeautifulSoup(html, 'html.parser')
data = []
current_company = None

# ステップ3: h2とulのセットごとに処理
for tag in soup.select('.revision-list > *'):
    if tag.name == 'h2':
        current_company = tag.text.strip()
    elif tag.name == 'ul':
        for li in tag.select('li.revision'):
            rev_type = li.select_one('.revision__type')
            rev_msg = li.select_one('.revision__message')
            rev_status = li.select_one('.revision__status')
            rev_lines = li.text.strip().splitlines()
            rev_lines = [line.strip() for line in rev_lines if line.strip()]

            # タイトルから交通機関を抽出
            matched_line = ''
            for line in rev_lines:
                if rev_type and rev_type.text in line:
                    matched_line = line
                    break
            if matched_line:
                transport_name = matched_line.replace(rev_type.text, '').strip()
            else:
                transport_name = current_company  # fallback

            # 日付抽出
            date_match = re.search(r'(\d{4}/\d{1,2}/\d{1,2}|20\d{2}年\d{1,2}月\d{1,2}日)', rev_msg.text)
            date_value = ''
            if date_match:
                try:
                    raw_date = date_match.group(1)
                    if '年' in raw_date:
                        date_value = datetime.strptime(raw_date, '%Y年%m月%d日').strftime('%Y/%m/%d')
                    else:
                        date_value = datetime.strptime(raw_date, '%Y/%m/%d').strftime('%Y/%m/%d')
                except:
                    date_value = raw_date

            data.append([
                transport_name,
                rev_type.text.strip() if rev_type else '',
                rev_msg.text.strip().replace('\n', ''),
                rev_status.text.strip() if rev_status else '',
                date_value
            ])

# ステップ4: 最新レコードの抽出（#2の処理）
df = pd.DataFrame(data, columns=['交通機関', '内容', '改定メッセージ', '対応状況', '改定日'])
df = df[df['対応状況'] == '対応済']
df = df[df['内容'] == '運賃改定']

# 最新日付をもつレコードだけ残す
df['改定日_date'] = pd.to_datetime(df['改定日'], errors='coerce')
df = df.dropna(subset=['改定日_date'])
df = df.sort_values('改定日_date', ascending=False)
df = df.drop_duplicates(subset=['交通機関', '内容'], keep='first')
df = df.drop(columns='改定日_date')

# ステップ5: CSV出力
df.to_csv('filtered_revision_data.csv', index=False, encoding='utf-8-sig')  # DataFrameをファイルに保存

# ダウンロード
files.download('filtered_revision_data.csv')
