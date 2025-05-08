import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import io

st.title("NAVITIME 改定情報 抽出アプリ（#4対応）")
st.write("HTMLファイルをアップロードすると、交通機関ごとの改定情報（最新・対応済み・運賃改定）をCSV形式で出力します。")

uploaded_file = st.file_uploader("HTMLファイルを選択してください", type=["html"])
if uploaded_file:
    html = uploaded_file.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    current_company = None

    for tag in soup.select('.revision-list > *'):
        if tag.name == 'h2':
            current_company = tag.text.strip()
        elif tag.name == 'ul':
            for li in tag.select('li.revision'):
                if not current_company:
                    continue
                line_name = li.select_one('.revision__line')
                rev_type = li.select_one('.revision__type')
                rev_msg = li.select_one('.revision__message')
                rev_status = li.select_one('.revision__status')
                if line_name and rev_type and rev_msg and rev_status:
                    data.append([
                        f"{current_company}{line_name.text.strip()}",
                        rev_type.text.strip(),
                        rev_msg.text.strip().replace('\n', ''),
                        rev_status.text.strip()
                    ])

    df = pd.DataFrame(data, columns=['交通機関', '内容', '改定メッセージ', '対応状況'])

    # フィルタリング：対応済 & 運賃改定 & 最新日付だけ
    df_filtered = df.copy()
    df_filtered = df_filtered[df_filtered['対応状況'] == '対応済']
    df_filtered = df_filtered[df_filtered['内容'] == '運賃改定']
    df_filtered['改定日'] = df_filtered['改定メッセージ'].str.extract(r'((?:20|19)\d{2}[^日)）\s]*)')
    df_filtered['改定日'] = pd.to_datetime(df_filtered['改定日'], errors='coerce')
    df_filtered = df_filtered.dropna(subset=['改定日'])
    df_filtered = df_filtered.sort_values('改定日').drop_duplicates(subset=['交通機関', '内容'], keep='last')
    df_filtered = df_filtered.drop(columns='改定日')

    st.subheader("抽出された改定情報（最新・対応済み・運賃改定）")
    st.dataframe(df_filtered)

    csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
    st.download_button("CSVをダウンロード", data=csv, file_name='filtered_revision.csv', mime='text/csv')
