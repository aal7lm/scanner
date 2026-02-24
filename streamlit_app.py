import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="رادار نيبولا V60", layout="wide")

st.title("🚀 رادار نيبولا - سوق الأسهم السعودية")
st.write("فحص فني مباشر لأهم 40 سهم في السوق بناءً على استراتيجية الانقضاض")

# قائمة الـ 40 سهم المحدثة
tickers = [
    "1120.SR", "2222.SR", "2010.SR", "1150.SR", "1180.SR", "7010.SR", "4030.SR", "2310.SR", "1211.SR", "2080.SR",
    "1010.SR", "1140.SR", "1080.SR", "1111.SR", "2030.SR", "4001.SR", "2280.SR", "4190.SR", "2020.SR", "2350.SR",
    "4260.SR", "6010.SR", "8010.SR", "1060.SR", "2050.SR", "4090.SR", "7020.SR", "1810.SR", "4160.SR", "6001.SR",
    "2060.SR", "1301.SR", "1320.SR", "4070.SR", "2120.SR", "4290.SR", "1123.SR", "2011.SR", "1020.SR", "2223.SR"
]

def check_signal(ticker):
    try:
        df = yf.download(ticker, period="60d", interval="1d", progress=False)
        if df.empty: return None
        
        # المعادلات
        df['EMA5'] = ta.ema(df['Close'], length=5)
        df['EMA21'] = ta.ema(df['Close'], length=21)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last = df.iloc[-1]
        
        # شرط الانقضاض
        is_attack = (last['EMA5'] > last['EMA21']) and (last['RSI'] > 50) and (last['Close'] > last['EMA21'])
        
        return {
            "السهم": ticker.replace(".SR", ""),
            "السعر": round(float(last['Close']), 2),
            "RSI": round(float(last['RSI']), 2),
            "الحالة": "🚀 جاهز" if is_attack else "⌛ انتظار"
        }
    except:
        return None

if st.button('تحديث البيانات الآن'):
    results = []
    bar = st.progress(0)
    for i, t in enumerate(tickers):
        res = check_signal(t)
        if res: results.append(res)
        bar.progress((i + 1) / len(tickers))
    
    df_final = pd.DataFrame(results)
    
    # تنسيق العرض
    def style_row(row):
        return ['color: #39FF14' if row['الحالة'] == "🚀 جاهز" else 'color: white'] * len(row)

    st.dataframe(df_final.style.apply(style_row, axis=1), use_container_width=True)
