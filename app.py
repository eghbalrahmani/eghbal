import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
import jdatetime

# تنظیمات صفحه
st.set_page_config(
    page_title="ردیاب عادت (شمسی)",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل‌دهی مدرن راست‌چین و شبیه‌سازی دقیق داشبورد
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Vazirmatn', sans-serif;
        direction: RTL;
        text-align: right;
        background-color: #f8fafc;
    }
    
    .glass-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
        margin-bottom: 25px;
        border: 1px solid #f1f5f9;
    }
    
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        text-align: center;
        margin-bottom: 5px;
    }
    
    .pov-text {
        font-size: 15px;
        color: #64748b;
        text-align: center;
        font-style: italic;
        margin-bottom: 30px;
    }
    
    .day-header {
        font-weight: bold;
        text-align: center;
        font-size: 11px;
        color: #475569;
    }
    .weekday-header {
        font-size: 9px;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2px;
    }
    
    .stCheckbox {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "habit_data.json"
SHAMSI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "habits": ["ورزش کردن 🏃‍♂️", "کتاب خواندن 📚", "تغذیه سالم 🥗", "کار عمیق 💻"],
        "history": {},
        "month": "فروردین",
        "year": "1405",
        "pov": "هر روز یک قدم به اهدافت نزدیک‌تر شو ✨"
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# --- هدر اصلی ---
st.markdown(f"<div class='main-title'>HABIT TRACKER</div>", unsafe_allow_html=True)
st.markdown(f"<div class='pov-text'>Pov: {data['pov']}</div>", unsafe_allow_html=True)

# سایدبار تنظیمات
st.sidebar.header("⚙️ تنظیمات تقویم")
selected_month = st.sidebar.selectbox("انتخاب ماه شمسی", SHAMSI_MONTHS, index=SHAMSI_MONTHS.index(data["month"]) if data["month"] in SHAMSI_MONTHS else 0)
selected_year = st.sidebar.text_input("سال شمسی", data["year"])
data["month"] = selected_month
data["year"] = selected_year
data["pov"] = st.sidebar.text_area("جمله انگیزشی (POV)", data["pov"])
save_data(data)

# محاسبه روزهای ماه شمسی
month_idx = SHAMSI_MONTHS.index(selected_month) + 1
if month_idx <= 6:
    days_count = 31
elif month_idx <= 11:
    days_count = 30
else:
    # اسفند (ساده‌سازی: ۲۹ روزه، بدون احتساب دقیق کبیسه فعلاً)
    days_count = 29

# محاسبه روزهای هفته برای بالای ستون‌ها
WEEKDAYS_FA = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
def get_shamsi_weekday_name(y, m, d):
    try:
        # ساخت آبجکت تاریخ شمسی و گرفتن روز هفته (۰ برای شنبه تا ۶ برای جمعه در jdatetime)
        j_date = jdatetime.date(int(y), m, d)
        return WEEKDAYS_FA[j_date.weekday()]
    except:
        return "-"

# --- محاسبات آمار و پیشرفت ---
history = data["history"]
habits = data["habits"]
total_possible = len(habits) * days_count
total_checked = 0

for d in range(1, days_count + 1):
    day_key = f"{selected_year}-{month_idx}-{d}"
    if day_key in history:
        for h in habits:
            if history[day_key].get(h, False):
                total_checked += 1

progress_pct = (total_checked / total_possible * 100) if total_possible > 0 else 0

# --- نمایش آمار با دونات چارت ---
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
stat_col1, stat_col2 = st.columns([1, 1])
with stat_col1:
    st.subheader("📊 خلاصه وضعیت پیشرفت ماه")
    st.metric(label="کل عادات تکمیل شده", value=f"{total_checked} از {total_possible}")
    st.metric(label="درصد موفقیت کلی", value=f"{progress_pct:.1f}%")
with stat_col2:
    fig = go.Figure(data=[go.Pie(
        labels=['کامل شده', 'باقی‌مانده'],
        values=[total_checked, max(0, total_possible - total_checked)],
        hole=.6,
        marker_colors=['#3b82f6', '#f1f5f9']
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=180,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- جدول اصلی عادات ---
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("📅 جدول ردیابی روزانه")

# افزودن عادت جدید
add_col1, add_col2 = st.columns([3, 1])
with add_col1:
    new_habit = st.text_input("ثبت عادت جدید:", placeholder="مثال: صبح زود بیدار شدن ⏰", key="add_habit_input")
with add_col2:
    st.write("")
    st.write("")
    if st.button("➕ افزودن"):
        if new_habit and new_habit not in habits:
            data["habits"].append(new_habit)
            save_data(data)
            st.rerun()

st.markdown("<hr style='border: 0.5px solid #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)

# رسم ستون‌های جدول
grid_cols = st.columns([3] + [1] * days_count)
grid_cols[0].markdown("<div style='font-weight: bold; font-size:13px;'>عنوان عادت</div>", unsafe_allow_html=True)

for d in range(1, days_count + 1):
    w_day = get_shamsi_weekday_name(selected_year, month_idx, d)
    grid_cols[d].markdown(
        f"<div class='weekday-header'>{w_day}</div>"
        f"<div class='day-header'>{d}</div>", 
        unsafe_allow_html=True
    )

for habit in habits:
    row_cols = st.columns([3] + [1] * days_count)
    
    with row_cols[0]:
        del_c, name_c = st.columns([1, 4])
        if del_c.button("❌", key=f"del_{habit}", help="حذف عادت"):
            data["habits"].remove(habit)
            # تمیزکاری رکوردها
            for k in list(data["history"].keys()):
                if habit in data["history"][k]:
                    del data["history"][k][habit]
            save_data(data)
            st.rerun()
        name_c.markdown(f"<div style='font-size: 13px; font-weight: 500; padding-top:4px;'>{habit}</div>", unsafe_allow_html=True)
        
    for d in range(1, days_count + 1):
        day_key = f"{selected_year}-{month_idx}-{d}"
        if day_key not in data["history"]:
            data["history"][day_key] = {}
        
        current_state = data["history"][day_key].get(habit, False)
        checked = row_cols[d].checkbox("", value=current_state, key=f"check_{habit}_{d}", label_visibility="collapsed")
        
        if checked != current_state:
            data["history"][day_key][habit] = checked
            save_data(data)
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
