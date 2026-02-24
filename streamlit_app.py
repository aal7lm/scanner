import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time  # استيراد مكتبة الوقت للالتفاف على الحظر

st.set_page_config(page_title="رادار نيبولا المطور", layout="wide")

st.title("🚀 رادار نيبولا - النسخة الذكية")
st.write("إذا ظهر خطأ في التحميل، انتظر قليلاً ثم اضغط التحديث مرة أخرى")

# قائمة مصغرة للتجربة وضمان العمل
tickers = ["1120.SR", "2222.SR", "2010.SR", "1150.SR", "1180.SR", "7010.SR", "4030.SR", "2170.SR", "1211.SR", "2083.SR"]

def check_signal(ticker):
    try:
        # جلب البيانات بهدوء
        data = yf.Ticker(ticker)
        df = data.history(period="60d")
        if df.empty: return None
        
        # الحسابات الفنية
        df['EMA5'] = ta.ema(df['Close'], length=5)
        df['EMA21'] = ta.ema(df['Close'], length=21)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last = df.iloc[-1]
        is_attack = (last['EMA5'] > last['EMA21']) and (last['RSI'] > 50)
        
        return {
            "السهم": ticker.replace(".SR", ""),
            "السعر": round(float(last['Close']), 2),
            "RSI": round(float(last['RSI']), 2),
            "الحالة": "🚀 جاهز" if is_attack else "⌛ انتظار"
        }
    except Exception as e:
        return None

if st.button('إطلاق الرادار الآن'):
    results = []
    progress_text = st.empty()
    bar = st.progress(0)
    
    for i, t in enumerate(tickers):
        progress_text.text(f"جاري فحص: {t} ...")
        res = check_signal(t)
        if res:
            results.append(res)
        bar.progress((i + 1) / len(tickers))
        time.sleep(1) # الانتظار ثانية واحدة لتجنب الحظر (Rate Limit)
    
    if results:
        df_final = pd.DataFrame(results)
        st.success("تم التحديث بنجاح!")
        st.table(df_final)
    else:
        st.error("خادم البيانات مشغول حالياً، يرجى المحاولة بعد دقيقة.")

