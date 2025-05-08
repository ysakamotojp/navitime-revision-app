import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import io

st.set_page_config(page_title="ダイヤ改正・運賃改定 抽出ツール", layout="wide")

st.title("ダイヤ改正・運賃改定情報 抽出ツール")
uploaded_file = st.file_uploader("HTMLファイルをアップロードしてください", type="html")

if uploaded_file:
    html_content = uploaded_file.read().decode("utf-8")
    soup = BeautifulSoup(html_content, 'html.parser')

    data = []
    current_company = None

    for tag in soup.select('.revision-list > *'):
        if tag.name == 'h2':
            current_company = tag.text.strip()
        elif tag.name == 'ul':
            for li in tag.select('li.revision'):
                # パターン2: <p class="revision__link"> で交通機関が指定されている場合
                link = li.select_one('.revision__link')
                company = link.text.strip() if link else current_company

                rev_type = li.select_one('.revision__type')
                rev_msg = li.select_one('.revision__message')
                rev_status = li.select_one('.revision__status')

                if rev_type and rev_msg and rev_status:
                    data.append([
                        company,
                        rev_type.text.strip(),
                        rev_msg.text.strip().replace('\n', ''),
                        rev_status.text.strip()
                    ])

    if data:
        df = pd.DataFrame(data, columns=["交通機関", "内容", "改定メッセージ", "対応状況"])
        st.success(f"{len(df)} 件のデータを抽出しました。")
        st.dataframe(df)

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        st.download_button(
            label="CSVをダウンロード",
            data=csv_buffer.getvalue(),
            file_name="revision_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("データが抽出できませんでした。HTMLの構造をご確認ください。")
