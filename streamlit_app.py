import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

st.set_page_config(page_title="رادار نيبولا برو V61", layout="wide")

st.title("🚀 رادار نيبولا الاحترافي - TASI")
st.subheader("تحليل السيولة، السعر العادل، وإشارات الانقضاض")

# القائمة الموسعة (يمكنك إضافة المزيد)
tickers = [
    "1120.SR", "2222.SR", "2010.SR", "1150.SR", "1180.SR", 
    "7010.SR", "4030.SR", "2310.SR", "1211.SR", "2080.SR",
    "1010.SR", "1140.SR", "1080.SR", "1111.SR", "2030.SR"
]

def analyze_stock(ticker):
    try:
        data = yf.Ticker(ticker)
        df = data.history(period="100d")
        if df.empty: return None
        
        # 1. المؤشرات الأساسية
        df['EMA5'] = ta.ema(df['Close'], length=5)
        df['EMA21'] = ta.ema(df['Close'], length=21)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # 2. حساب السعر العادل (نقطة الارتكاز)
        fair_price = df['Close'].rolling(window=20).mean().iloc[-1]
        
        # 3. حساب قوة السيولة (Volume Boost)
        avg_vol = df['Volume'].rolling(window=20).mean().iloc[-1]
        current_vol = df['Volume'].iloc[-1]
        vol_ratio = (current_vol / avg_vol) * 100
        
        last = df.iloc[-1]
        close_p = last['Close']
        
        # 4. تحديد التقييم
        valuation = "💎 رخيص" if close_p < fair_price * 0.95 else "🔥 متضخم" if close_p > fair_price * 1.05 else "⚖️ عادل"
        
        # 5. شرط الانقضاض المطور
        is_attack = (last['EMA5'] > last['EMA21']) and (last['RSI'] > 52) and (close_p > last['EMA21'])
        
        return {
            "السهم": ticker.replace(".SR", ""),
            "السعر": round(float(close_p), 2),
            "السعر العادل": round(float(fair_price), 2),
            "التقييم": valuation,
            "RSI": round(float(last['RSI']), 1),
            "قوة السيولة": f"{int(vol_ratio)}%",
            "الحالة": "🚀 انقضاض" if is_attack else "⌛ انتظار"
        }
    except:
        return None

if st.button('تحديث الرادار المطور ⚡'):
    results = []
    bar = st.progress(0)
    status_text = st.empty()
    
    for i, t in enumerate(tickers):
        status_text.text(f"تحليل السهم {i+1} من {len(tickers)}...")
        res = analyze_stock(t)
        if res: results.append(res)
        bar.progress((i + 1) / len(tickers))
        time.sleep(0.5)
    
    if results:
        df_final = pd.DataFrame(results)
        
        # وظيفة تلوين الصفوف
        def highlight_attack(row):
            if row['الحالة'] == "🚀 انقضاض":
                return ['background-color: #1b4d3e; color: #39FF14'] * len(row)
            return [''] * len(row)

        st.dataframe(df_final.style.apply(highlight_attack, axis=1), use_container_width=True)
        st.success("تم التحديث! الأسهم باللون الأخضر الداكن هي الأقرب للانفجار.")
