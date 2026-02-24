import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

st.set_page_config(page_title="رادار نيبولا للسيولة V62", layout="wide")

st.title("🚀 رادار نيبولا - كاشف السيولة والتجميع")

# القائمة (يمكنك زيادتها)
tickers = ["1120.SR", "2222.SR", "2010.SR", "1150.SR", "7010.SR", "1180.SR", "4030.SR", "1211.SR", "2080.SR", "1010.SR"]

def get_liquidity_analysis(ticker):
    try:
        data = yf.Ticker(ticker)
        df = data.history(period="100d")
        if df.empty or len(df) < 30: return None
        
        # 1. حساب السيولة (MFI) - Money Flow Index
        df['MFI'] = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=14)
        
        # 2. مؤشر التراكم والتوزيع (ADL) لمعرفة التجميع
        # ببساطة: إذا أغلق السهم قريباً من الهاي بسيولة عالية = تجميع
        df['EMA21'] = ta.ema(df['Close'], length=21)
        
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        # حساب نسبة السيولة مقارنة بـ 20 يوم
        avg_vol = df['Volume'].tail(20).mean()
        vol_ratio = (last_row['Volume'] / avg_vol) * 100
        
        # منطق التجميع والتصريف
        m_range = last_row['High'] - last_row['Low']
        close_pos = (last_row['Close'] - last_row['Low']) / m_range if m_range != 0 else 0.5
        
        if close_pos > 0.7 and last_row['Volume'] > avg_vol:
            flow_type = "🟢 تجميع قوي"
        elif close_pos < 0.3 and last_row['Volume'] > avg_vol:
            flow_type = "🔴 تصريف/بيع"
        else:
            flow_type = "🟡 تذبذب هادئ"

        # إشارة الانقضاض
        is_attack = (last_row['MFI'] > 50) and (last_row['Close'] > df['EMA21'].iloc[-1])
        
        return {
            "السهم": ticker.replace(".SR", ""),
            "السعر": round(last_row['Close'], 2),
            "تدفق السيولة (MFI)": int(last_row['MFI']),
            "حجم السيولة": f"{int(vol_ratio)}%",
            "نوع الحركة": flow_type,
            "الحالة": "🚀 انقضاض" if is_attack else "⌛ انتظار"
        }
    except:
        return None

if st.button('فحص السيولة الآن 🔍'):
    results = []
    progress_bar = st.progress(0)
    for i, t in enumerate(tickers):
        res = get_liquidity_analysis(t)
        if res: results.append(res)
        progress_bar.progress((i + 1) / len(tickers))
        time.sleep(0.4)
    
    if results:
        df_final = pd.DataFrame(results)
        
        def color_flow(val):
            if "تجميع" in str(val): return 'background-color: #004d00; color: white'
            if "تصريف" in str(val): return 'background-color: #4d0000; color: white'
            return ''

        st.dataframe(df_final.style.applymap(color_flow, subset=['نوع الحركة']), use_container_width=True)
        st.info("💡 نصيحة: السهم الذي يجمع بين (تجميع قوي) و (انقضاض) هو الأفضل للدخول.")
