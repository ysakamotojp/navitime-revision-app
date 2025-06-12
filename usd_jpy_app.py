import streamlit as st
import requests
import sqlite3
from datetime import datetime

# Database initialization
conn = sqlite3.connect('usd_jpy.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS rates
             (timestamp TEXT, rate REAL)''')
conn.commit()

st.title("ドル円相場取得アプリ")

# Session state to store rate
if 'rate' not in st.session_state:
    st.session_state['rate'] = None

if st.button('確認'):
    try:
        resp = requests.get('https://api.exchangerate.host/latest?base=USD&symbols=JPY')
        if resp.status_code == 200:
            data = resp.json()
            st.session_state['rate'] = data['rates']['JPY']
            st.success(f"現在のドル円相場: {st.session_state['rate']}")
        else:
            st.error('為替情報の取得に失敗しました')
    except Exception as e:
        st.error('為替情報の取得中にエラーが発生しました')

if st.session_state['rate'] is not None:
    if st.button('登録'):
        now = datetime.utcnow().isoformat()
        c.execute('INSERT INTO rates (timestamp, rate) VALUES (?, ?)', (now, st.session_state['rate']))
        conn.commit()
        st.success('DBに登録しました')

# Display stored data
if st.checkbox('登録済みデータを表示'):
    rows = c.execute('SELECT * FROM rates ORDER BY timestamp DESC').fetchall()
    if rows:
        for ts, rate in rows:
            st.write(f"{ts}: {rate}")
    else:
        st.write('データがありません')
