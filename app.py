import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re
import datetime

st.title("改定情報抽出アプリ")

uploaded_file = st.file_uploader("HTMLファイルをアップロードしてください", type=["html"])

if uploaded_file is not None:
    soup = BeautifulSoup(uploaded_file.read(), 'html.parser')
    data = []
    current_company = None

    for tag in soup.select('.revision-list > *'):
        if tag.name == 'h2':
            current_company = tag.text.strip()
        elif tag.name == 'ul':
            for li in tag.select('li.revision'):
                if not current_company:
                    continue
                rev_type = li.select_one('.revision__type')
                rev_msg = li.select_one('.revision__message')
                rev_status = li.select_one('.revision__status')
                line_name_tag = li.select_one('p.revision__link')

                if rev_type and rev_msg and rev_status:
                    line_name = line_name_tag.text.strip() if line_name_tag else current_company
                    content = rev_type.text.strip()
                    message = rev_msg.text.strip().replace('\n', '')
                    status = rev_status.text.strip()
                    data.append([line_name, content, message, status])

    df = pd.DataFrame(data, columns=['交通機関', '内容', '改定メッセージ', '対応状況'])

    # 日付抽出関数
    def extract_date(text):
        match = re.search(r'(\d{4})[年/]?(\d{1,2})[月/]?(\d{1,2})?', text)
        if match:
            y, m, d = match.groups()
            try:
                date_obj = datetime.date(int(y), int(m), int(d) if d else 1)
                return date_obj.strftime('%Y/%m/%d')
            except:
                return None
        return None

    # 対象のフィルタ処理
    df_filtered = df[(df['対応状況'] == '対応済') & (df['内容'] == '運賃改定')].copy()
    df_filtered['日付'] = df_filtered['改定メッセージ'].apply(extract_date)

    latest_df = df_filtered.sort_values('日付', ascending=False).drop_duplicates(subset=['交通機関', '内容'])
    latest_df = latest_df[['交通機関', '内容', '改定メッセージ', '日付', '対応状況']]

    st.subheader("抽出結果（対応済かつ運賃改定・最新日付のみ）")
    st.dataframe(latest_df)

    csv = latest_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="CSVをダウンロード",
        data=csv,
        file_name='filtered_revision_info.csv',
        mime='text/csv'
    )
