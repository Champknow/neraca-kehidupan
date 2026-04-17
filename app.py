import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Neraca Kehidupan", page_icon="📊", layout="wide")

# =============================================
# CUSTOM CSS (CLEAN & SIMPLE)
# =============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .accent-bar {
        height: 4px;
        border-radius: 2px;
        margin-bottom: 16px;
    }
    .bar-green { background: #1D9E75; }
    .bar-amber { background: #EF9F27; }
    .bar-blue { background: #378ADD; }
    .bar-coral { background: #D85A30; }
    
    .metric-label {
        font-size: 0.75rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #1F2937;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    .badge-green { background: #EAF3DE; color: #3B6D11; }
    .badge-amber { background: #FAEEDA; color: #854F0B; }
    .badge-blue { background: #E6F1FB; color: #185FA5; }
    .badge-red { background: #FCEBEB; color: #A32D2D; }
    
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 16px;
    }
    
    .habit-dot {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        margin: 0 auto;
        cursor: pointer;
        transition: all 0.15s;
        border: 2px solid transparent;
    }
    .habit-dot:hover {
        transform: scale(1.1);
    }
    
    .mood-circle {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        cursor: pointer;
        transition: all 0.2s;
        border: 3px solid transparent;
        margin: 0 auto;
    }
    .mood-circle:hover {
        transform: scale(1.1);
    }
    .mood-circle.active {
        border-color: #1D9E75;
        box-shadow: 0 4px 12px rgba(29, 158, 117, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# FUNGSI DATA (SUDAH DIPERBAIKI)
# =============================================
def load_categories():
    path = "data/categories.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df = pd.DataFrame(columns=["id", "name", "type", "budget"])
        df.to_csv(path, index=False)
        return df

def save_categories(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/categories.csv", index=False)

def load_transactions():
    path = "data/transactions.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        return df
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df = pd.DataFrame(columns=["id", "type", "category", "amount", "date", "note"])
        df.to_csv(path, index=False)
        return df

def save_transaction(trans_type, category, amount, date, note):
    os.makedirs("data", exist_ok=True)
    df = load_transactions()
    if df.empty:
        new_id = "TRX001"
    else:
        last_id = df["id"].iloc[-1]
        num = int(last_id[3:]) + 1
        new_id = f"TRX{num:03d}"
    new_row = pd.DataFrame([{
        "id": new_id,
        "type": trans_type,
        "category": category,
        "amount": amount,
        "date": date.strftime("%Y-%m-%d"),
        "note": note
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("data/transactions.csv", index=False)

def load_habits():
    path = "data/habits.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        dates = [start_of_week + timedelta(days=i) for i in range(7)]
        habits = ["Olahraga", "Baca buku", "Belajar coding"]
        data = []
        for habit in habits:
            for d in dates:
                data.append({"habit_name": habit, "date": d.strftime("%Y-%m-%d"), "status": 0})
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)
        return df

def save_habit_status(habit_name, date_str, status):
    os.makedirs("data", exist_ok=True)
    df = load_habits()
    mask = (df['habit_name'] == habit_name) & (df['date'] == date_str)
    if not df[mask].empty:
        df.loc[mask, 'status'] = status
    else:
        new_row = pd.DataFrame([{"habit_name": habit_name, "date": date_str, "status": status}])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("data/habits.csv", index=False)

def load_goals():
    path = "data/goals.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df = pd.DataFrame([
            {"id": "GOAL001", "name": "Selesai project n8n", "target": 100, "current": 90, "unit": "%", "icon": "💻", "color": "#1D9E75"},
            {"id": "GOAL002", "name": "Baca 2 buku", "target": 2, "current": 1, "unit": "buku", "icon": "📚", "color": "#378ADD"},
            {"id": "GOAL003", "name": "Nabung 1 juta", "target": 1000000, "current": 320000, "unit": "Rp", "icon": "💰", "color": "#EF9F27"}
        ])
        df.to_csv(path, index=False)
        return df

def save_goals(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/goals.csv", index=False)

# =============================================
# SIDEBAR
# =============================================
st.sidebar.title("Neraca Kehidupan")
menu = st.sidebar.radio("Menu", ["🏠 Dashboard", "📋 Transaksi", "📊 Anggaran", "📂 Riwayat"])

# =============================================
# DASHBOARD
# =============================================
if menu == "🏠 Dashboard":
    # Header
    col_logo, col_date = st.columns([3, 1])
    with col_logo:
        st.markdown("""
        <div style="font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700; letter-spacing: -0.5px;">
            neraca_<span style="color: #1D9E75;">kehidupan</span>
        </div>
        """, unsafe_allow_html=True)
    with col_date:
        today_str = datetime.now().strftime("%A, %d %B %Y")
        st.markdown(f"""
        <div style="text-align: right; font-size: 0.8rem; color: #6B7280; background: #F9FAFB; padding: 6px 12px; border-radius: 20px; border: 1px solid #E5E7EB;">
            {today_str}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Load data
    df_trans = load_transactions()
    df_cat = load_categories()
    df_habits = load_habits()
    df_goals = load_goals()

    # Proses delete goal dari query params
    query_params = st.query_params
    if "delete_goal" in query_params:
        goal_id_to_delete = query_params["delete_goal"]
        df_goals = df_goals[df_goals['id'] != goal_id_to_delete]
        save_goals(df_goals)
        st.query_params.clear()
        st.rerun()

    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    if not df_trans.empty:
        df_bulan_ini = df_trans[df_trans['date'].dt.date >= start_of_month]
        pemasukan = df_bulan_ini[df_bulan_ini['type'] == 'Pemasukan']['amount'].sum()
        pengeluaran = df_bulan_ini[df_bulan_ini['type'] == 'Pengeluaran']['amount'].sum()
        saldo_bulan_ini = pemasukan - pengeluaran
    else:
        saldo_bulan_ini = 0
        df_bulan_ini = pd.DataFrame()
    
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    mask_minggu_ini = (pd.to_datetime(df_habits['date']).dt.date >= start_of_week) & (pd.to_datetime(df_habits['date']).dt.date <= end_of_week)
    df_week = df_habits[mask_minggu_ini]
    if not df_week.empty:
        total_habits = len(df_week)
        done = df_week['status'].sum()
        productivity = int((done / total_habits) * 100) if total_habits > 0 else 0
    else:
        productivity = 0
    
    completed_goals = sum(df_goals['current'] >= df_goals['target'])
    total_goals = len(df_goals)
    
    # Greeting
    st.markdown("## Halo, Fikri!")
    today_str = today.strftime("%Y-%m-%d")
    today_habits = df_habits[df_habits['date'] == today_str]
    if not today_habits.empty:
        total_today = len(today_habits)
        done_today = today_habits['status'].sum()
        pct_today = int((done_today / total_today) * 100) if total_today > 0 else 0
    else:
        pct_today = 0
    st.caption(f"Hari ini lu udah {pct_today}% on track. Let's push it.")
    
    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container():
            st.markdown('<div class="accent-bar bar-green"></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Saldo bulan ini</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">Rp {saldo_bulan_ini/1e6:.1f}jt</div>', unsafe_allow_html=True)
            st.markdown('<span class="badge badge-green">+12%</span>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="accent-bar bar-amber"></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Habit streak</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{productivity}%</div>', unsafe_allow_html=True)
            st.markdown('<span class="badge badge-amber">minggu ini</span>', unsafe_allow_html=True)
    with col3:
        with st.container():
            st.markdown('<div class="accent-bar bar-blue"></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Goals selesai</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{completed_goals}/{total_goals}</div>', unsafe_allow_html=True)
            st.markdown('<span class="badge badge-blue">bulan ini</span>', unsafe_allow_html=True)
    with col4:
        mood_score = st.session_state.get("mood_score", 7.0)
        if mood_score >= 8.5:
            badge_text = "🔥 on fire"
            badge_class = "badge-amber"
        elif mood_score >= 7.0:
            badge_text = "😊 baik"
            badge_class = "badge-green"
        elif mood_score >= 5.0:
            badge_text = "😐 biasa"
            badge_class = "badge-blue"
        else:
            badge_text = "😩 burnout"
            badge_class = "badge-red"
        with st.container():
            st.markdown('<div class="accent-bar bar-coral"></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Mood minggu ini</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{mood_score}</div>', unsafe_allow_html=True)
            st.markdown(f'<span class="badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2: Habit Tracker, Chart, Goals
    col_left, col_mid, col_right = st.columns([1.2, 1.2, 1])
    
    # ------------------ HABIT TRACKER (AUTO-SAVE VIA QUERY PARAMS) ------------------
    with col_left:
        st.markdown('<div class="section-title">Habit Tracker — minggu ini</div>', unsafe_allow_html=True)
        
        habits_list = ["Olahraga", "Baca buku", "Belajar coding"]
        dates = [start_of_week + timedelta(days=i) for i in range(7)]
        day_labels = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
        
        # Proses klik dari query params
        query_params = st.query_params
        if "habit_click" in query_params:
            habit, date_str = query_params["habit_click"].split("|")
            # Toggle status
            status_row = df_habits[(df_habits['habit_name'] == habit) & (df_habits['date'] == date_str)]
            current = 0 if status_row.empty else int(status_row['status'].iloc[0])
            save_habit_status(habit, date_str, 1 if current == 0 else 0)
            st.query_params.clear()
            st.rerun()
        
        for habit in habits_list:
            st.markdown(f'<p style="font-size: 13px; font-weight: 500; color: #4B5563; margin: 16px 0 8px 0;">{habit}</p>', unsafe_allow_html=True)
            
            cols = st.columns(7)
            for i, d in enumerate(dates):
                date_str = d.strftime("%Y-%m-%d")
                status_row = df_habits[(df_habits['habit_name'] == habit) & (df_habits['date'] == date_str)]
                is_done = False if status_row.empty else (int(status_row['status'].iloc[0]) == 1)
                is_today = (d == today)
                
                if is_done:
                    bg_color = "#2DD4BF"
                    border_color = "#14B8A6"
                elif is_today:
                    bg_color = "#FBBF24"
                    border_color = "#F59E0B"
                else:
                    bg_color = "#F3F4F6"
                    border_color = "#E5E7EB"
                
                with cols[i]:
                    # Link dengan query param
                    st.markdown(f"""
<a href="?habit_click={habit}|{date_str}" target="_self" style="text-decoration: none;">
    <div class="habit-dot" style="background-color: {bg_color}; border-color: {border_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"></div>
</a>
<div style="text-align: center; font-size: 10px; color: #6B7280; margin-top: 4px;">{day_labels[i]}</div>
""", unsafe_allow_html=True)
    
    # ------------------ CHART ------------------
    with col_mid:
        st.markdown('<div class="section-title">Pengeluaran vs Pemasukan</div>', unsafe_allow_html=True)
        if not df_trans.empty:
            df_trans_copy = df_trans.copy()
            df_trans_copy['month'] = df_trans_copy['date'].dt.to_period('M')
            monthly = df_trans_copy.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
            if not monthly.empty:
                last_6 = monthly.tail(6).reset_index()
                last_6['month'] = last_6['month'].astype(str)
                pemasukan_vals = last_6['Pemasukan'].tolist() if 'Pemasukan' in last_6.columns else [0] * len(last_6)
                pengeluaran_vals = last_6['Pengeluaran'].tolist() if 'Pengeluaran' in last_6.columns else [0] * len(last_6)
                fig = go.Figure()
                fig.add_trace(go.Bar(x=last_6['month'], y=pemasukan_vals, name='Pemasukan', marker_color='#1D9E75'))
                fig.add_trace(go.Bar(x=last_6['month'], y=pengeluaran_vals, name='Pengeluaran', marker_color='#E24B4A'))
                fig.update_layout(barmode='group', height=250, margin=dict(l=0, r=0, t=10, b=0),
                                  legend=dict(orientation='h', yanchor='bottom', y=1.02),
                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Data bulanan belum tersedia.")
        else:
            st.info("Tambahkan transaksi untuk melihat grafik.")
    
    # ------------------ GOALS (AUTO-SAVE + DELETE) ------------------
    with col_right:
        st.markdown('<div class="section-title">Goals bulan ini</div>', unsafe_allow_html=True)
        
        if 'goals_temp' not in st.session_state:
            st.session_state.goals_temp = {}
        for _, row in df_goals.iterrows():
            goal_id = row['id']
            if goal_id not in st.session_state.goals_temp:
                st.session_state.goals_temp[goal_id] = row['current']
        
        changes_made = False
        for idx, row in df_goals.iterrows():
            goal_id = row['id']
            current_val = st.session_state.goals_temp[goal_id]
            progress_pct = min(current_val / row['target'], 1.0) if row['target'] > 0 else 0
            
            col_icon, col_text, col_pct, col_del = st.columns([0.15, 0.60, 0.15, 0.10])
            with col_icon:
                st.markdown(f"""
                <div style="width: 36px; height: 36px; border-radius: 10px; background: {row.get('color', '#EAF3DE')};
                            display: flex; align-items: center; justify-content: center; font-size: 18px;">
                    {row['icon']}
                </div>
                """, unsafe_allow_html=True)
            with col_text:
                st.markdown(f'<p style="font-weight: 500; margin-bottom: 3px; font-size: 13px;">{row["name"]}</p>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="height: 6px; background: #E5E7EB; border-radius: 3px; overflow: hidden; margin-bottom: 2px;">
                    <div style="width: {progress_pct*100}%; height: 100%; background: {row.get('color', '#1D9E75')}; border-radius: 3px;"></div>
                </div>
                """, unsafe_allow_html=True)
                new_val = st.slider(
                    f"Progress {row['name']}",
                    min_value=0, max_value=row['target'],
                    value=int(current_val),
                    step=max(1, int(row['target']/20)),
                    label_visibility="collapsed",
                    key=f"goal_slider_{goal_id}_{idx}"
                )
                if new_val != current_val:
                    st.session_state.goals_temp[goal_id] = new_val
                    changes_made = True
            with col_pct:
                color_pct = '#1D9E75' if progress_pct >= 0.9 else row.get('color', '#1F2937')
                st.markdown(f"""
                <div style="text-align: right; font-family: 'Space Mono', monospace; font-weight: 700; font-size: 13px; color: {color_pct};">
                    {int(progress_pct*100)}%
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                # Tombol hapus (X) dengan link query param
                st.markdown(f"""
                <a href="?delete_goal={goal_id}" target="_self" style="text-decoration: none;">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #FEE2E2; color: #EF4444;
                                display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700;
                                margin: 0 auto; cursor: pointer; transition: all 0.15s;"
                         onmouseover="this.style.background='#FECACA'" onmouseout="this.style.background='#FEE2E2'">
                        ✕
                    </div>
                </a>
                """, unsafe_allow_html=True)
            
            if idx < len(df_goals) - 1:
                st.markdown("<hr style='margin: 12px 0; opacity: 0.3;'>", unsafe_allow_html=True)
        
        if changes_made:
            for idx, row in df_goals.iterrows():
                goal_id = row['id']
                if goal_id in st.session_state.goals_temp:
                    df_goals.at[idx, 'current'] = st.session_state.goals_temp[goal_id]
            save_goals(df_goals)
            st.rerun()
        
        with st.expander("➕ Tambah Goal"):
            with st.form("new_goal_form"):
                goal_name = st.text_input("Nama Goal")
                goal_target = st.number_input("Target", min_value=1, value=100)
                goal_unit = st.text_input("Satuan", value="%")
                goal_icon = st.text_input("Ikon (emoji)", value="🎯")
                goal_color = st.color_picker("Warna", "#1D9E75")
                if st.form_submit_button("Simpan Goal"):
                    if goal_name:
                        new_id = f"GOAL{len(df_goals)+1:03d}"
                        new_row = pd.DataFrame([{
                            "id": new_id, "name": goal_name, "target": goal_target, "current": 0,
                            "unit": goal_unit, "icon": goal_icon, "color": goal_color
                        }])
                        df_goals = pd.concat([df_goals, new_row], ignore_index=True)
                        save_goals(df_goals)
                        st.success(f"Goal '{goal_name}' ditambahkan!")
                        if 'goals_temp' in st.session_state:
                            del st.session_state.goals_temp
                        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 3: Mood & Life Balance + Ringkasan Keuangan
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="section-title">Mood check hari ini</div>', unsafe_allow_html=True)
        
        mood_data = [
            {"emoji": "😩", "label": "Burnout", "score": 4.0, "bg": "#FCEBEB"},
            {"emoji": "😐", "label": "Biasa", "score": 5.0, "bg": "#FAEEDA"},
            {"emoji": "😊", "label": "Oke", "score": 7.0, "bg": "#EAF3DE"},
            {"emoji": "🔥", "label": "Produktif", "score": 8.5, "bg": "#E6F1FB"},
            {"emoji": "🚀", "label": "On fire", "score": 9.5, "bg": "#EEEDFE"}
        ]
        
        query_params = st.query_params
        if "mood_click" in query_params:
            st.session_state.mood_score = float(query_params["mood_click"])
            st.query_params.clear()
            st.rerun()
        
        current_mood_score = st.session_state.get("mood_score", 7.0)
        cols = st.columns(len(mood_data))
        for i, mood in enumerate(mood_data):
            with cols[i]:
                is_active = (current_mood_score == mood["score"])
                active_class = "active" if is_active else ""
                st.markdown(f"""
<a href="?mood_click={mood['score']}" target="_self" style="text-decoration: none;">
    <div class="mood-circle {active_class}" style="background: {mood['bg']};">
        {mood['emoji']}
    </div>
</a>
<p style="font-size: 0.65rem; margin-top: 4px; color: #6B7280; text-align: center;">{mood['label']}</p>
""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Life balance score</div>', unsafe_allow_html=True)

        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        df_bulan_ini = df_trans[df_trans['date'].dt.date >= start_of_month] if not df_trans.empty else pd.DataFrame()
        total_pemasukan = df_bulan_ini[df_bulan_ini['type'] == 'Pemasukan']['amount'].sum() if not df_bulan_ini.empty else 0
        total_pengeluaran = df_bulan_ini[df_bulan_ini['type'] == 'Pengeluaran']['amount'].sum() if not df_bulan_ini.empty else 0
        sisa = total_pemasukan - total_pengeluaran

        olahraga_week = df_week[df_week['habit_name'] == 'Olahraga']
        kesehatan_score = int((olahraga_week['status'].sum() / len(olahraga_week)) * 100) if not olahraga_week.empty else 0
        keuangan_score = max(0, min(100, int((sisa / total_pemasukan) * 100))) if total_pemasukan > 0 else 0
        coding_week = df_week[df_week['habit_name'] == 'Belajar coding']
        karir_score = int((coding_week['status'].sum() / len(coding_week)) * 100) if not coding_week.empty else 0
        sosial_week = df_week[df_week['habit_name'] == 'Baca buku']
        sosial_score = int((sosial_week['status'].sum() / len(sosial_week)) * 100) if not sosial_week.empty else 0

        balance_items = [
            ("Kesehatan", kesehatan_score, "#1D9E75"),
            ("Keuangan", keuangan_score, "#EF9F27"),
            ("Karir", karir_score, "#378ADD"),
            ("Sosial", sosial_score, "#D85A30")
        ]

        for label, score, color in balance_items:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 12px; color: #6B7280; width: 80px;">{label}</span>
                <div style="flex: 1; height: 6px; background: #E5E7EB; border-radius: 3px; overflow: hidden;">
                    <div style="width: {score}%; height: 100%; background: {color}; border-radius: 3px;"></div>
                </div>
                <span style="font-family: 'Space Mono', monospace; font-size: 11px; color: #6B7280; width: 30px; text-align: right;">{score}%</span>
            </div>
            """, unsafe_allow_html=True)
        # --- PROGRESS ANGGARAN BULAN INI ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Progress Anggaran</div>', unsafe_allow_html=True)
        
        if not df_bulan_ini.empty:
            # Ambil data pengeluaran per kategori bulan ini
            df_pengeluaran = df_bulan_ini[df_bulan_ini['type'] == 'Pengeluaran']
            pengeluaran_per_kat = df_pengeluaran.groupby('category')['amount'].sum().to_dict()
            
            # Loop kategori yang punya budget > 0
            for _, row in df_cat.iterrows():
                if row['type'] == 'Pengeluaran' and row['budget'] > 0:
                    spent = pengeluaran_per_kat.get(row['name'], 0)
                    budget = row['budget']
                    pct = min(spent / budget, 1.0) if budget > 0 else 0
                    color = "#EF4444" if pct > 0.9 else "#3B82F6" if pct > 0.7 else "#10B981"
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                            <span style="color: #4B5563;">{row['name']}</span>
                            <span style="font-family: 'Space Mono', monospace; color: #1F2937;">
                                Rp {spent:,.0f} / Rp {budget:,.0f}
                            </span>
                        </div>
                        <div style="height: 6px; background: #E5E7EB; border-radius: 3px; overflow: hidden;">
                            <div style="width: {pct*100}%; height: 100%; background: {color}; border-radius: 3px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Tambahkan transaksi untuk melihat progress anggaran.")
    with col_b:
        st.markdown('<div class="section-title">Ringkasan keuangan</div>', unsafe_allow_html=True)

        if not df_trans.empty and not df_bulan_ini.empty:
            df_pengeluaran = df_bulan_ini[df_bulan_ini['type'] == 'Pengeluaran']
            total_pemasukan = df_bulan_ini[df_bulan_ini['type'] == 'Pemasukan']['amount'].sum()
            total_pengeluaran = df_pengeluaran['amount'].sum()
            sisa = total_pemasukan - total_pengeluaran

            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <span style="color: #6B7280;">Pemasukan</span>
                <span style="font-family: 'Space Mono', monospace; font-weight: 700; color: #1D9E75;">+ Rp {total_pemasukan:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)

            for cat in df_pengeluaran['category'].unique():
                amount = df_pengeluaran[df_pengeluaran['category'] == cat]['amount'].sum()
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding-left: 10px;">
                    <span style="color: #6B7280;">{cat}</span>
                    <span style="font-family: 'Space Mono', monospace; font-weight: 700; color: #E24B4A;">- Rp {amount:,.0f}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<hr style='margin: 16px 0; opacity: 0.3;'>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; font-weight: 600; margin-bottom: 16px;">
                <span>Sisa bulan ini</span>
                <span style="font-family: 'Space Mono', monospace; color: #1D9E75;">Rp {sisa:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)

            target_tabungan = 4500000
            current_tabungan = sisa if sisa > 0 else 2980000
            progress = min(current_tabungan / target_tabungan, 1.0) if target_tabungan > 0 else 0
            st.markdown(f"""
            <div style="font-size: 11px; color: #6B7280; margin-bottom: 6px;">Tabungan progress</div>
            <div style="height: 8px; background: #E5E7EB; border-radius: 4px; overflow: hidden; margin-bottom: 4px;">
                <div style="width: {progress*100}%; height: 100%; background: linear-gradient(90deg, #1D9E75, #5DCAA5); border-radius: 4px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 11px;">
                <span style="color: #6B7280;">Target: Rp {target_tabungan:,.0f}</span>
                <span style="font-family: 'Space Mono', monospace; color: #1D9E75;">{progress*100:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Tambahkan transaksi untuk melihat ringkasan.")

# =============================================
# MENU LAINNYA
# =============================================
elif menu == "📋 Transaksi":
    st.title("Tambah Transaksi Baru")
    df_cat = load_categories()
    if df_cat.empty:
        st.warning("Data kategori belum tersedia. Silakan tambahkan di menu Anggaran.")
    else:
        with st.form("form_transaksi"):
            trans_type = st.radio("Tipe Transaksi", ["Pemasukan", "Pengeluaran"], horizontal=True)
            list_cat = df_cat[df_cat['type'] == trans_type]['name'].tolist()
            
            if not list_cat:
                st.error(f"⚠️ Belum ada kategori untuk tipe {trans_type}. Silakan tambahkan di menu Anggaran terlebih dahulu.")
                category = None
                amount = None
                date = None
                note = None
            else:
                category = st.selectbox("Kategori", list_cat)
                amount = st.number_input("Jumlah (Rp)", min_value=1000, step=1000, value=10000)
                date = st.date_input("Tanggal", value=datetime.now().date())
                note = st.text_input("Catatan (Opsional)")
            
            # Submit button selalu ada di luar blok if, tapi hanya diproses jika kategori tersedia
            submitted = st.form_submit_button("💾 Simpan Transaksi")
            if submitted:
                if list_cat:
                    save_transaction(trans_type, category, amount, date, note)
                    st.success(f"Transaksi {trans_type} sebesar Rp {amount:,.0f} berhasil disimpan!")
                    st.balloons()
                else:
                    st.error("Tidak dapat menyimpan transaksi karena kategori belum tersedia.")

elif menu == "📊 Anggaran":
    st.title("Kelola Kategori & Anggaran")
    df_cat = load_categories()
    with st.expander("➕ Tambah Kategori Baru"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Nama Kategori")
            new_type = st.selectbox("Tipe", ["Pemasukan", "Pengeluaran"])
        with col2:
            new_budget = st.number_input("Anggaran Bulanan (Rp)", min_value=0, step=10000, value=0)
        if st.button("Simpan Kategori"):
            if new_name:
                new_id = f"CAT{len(df_cat)+1:03d}"
                new_row = pd.DataFrame([{"id": new_id, "name": new_name, "type": new_type, "budget": new_budget}])
                df_cat = pd.concat([df_cat, new_row], ignore_index=True)
                save_categories(df_cat)
                st.success(f"Kategori {new_name} ditambahkan!")
                st.rerun()
            else:
                st.error("Nama kategori harus diisi.")
    st.subheader("Daftar Kategori")
    edited_df = st.data_editor(
        df_cat,
        column_config={
            "id": "ID",
            "name": "Nama Kategori",
            "type": "Tipe",
            "budget": st.column_config.NumberColumn("Anggaran (Rp)", format="Rp %d")
        },
        hide_index=True,
        num_rows="dynamic",
        disabled=["id"]
    )
    if st.button("💾 Simpan Perubahan"):
        save_categories(edited_df)
        st.success("Data kategori diperbarui!")
        st.rerun()

elif menu == "📂 Riwayat":
    st.title("Riwayat Transaksi")
    df_trans = load_transactions()
    if df_trans.empty:
        st.info("Belum ada transaksi.")
    else:
        months = sorted(df_trans['date'].dt.to_period('M').unique(), reverse=True)
        selected_month = st.selectbox("Filter Bulan", ["Semua"] + [str(m) for m in months])
        if selected_month != "Semua":
            df_filtered = df_trans[df_trans['date'].dt.to_period('M') == selected_month]
        else:
            df_filtered = df_trans
        display_df = df_filtered.copy()
        display_df['date'] = display_df['date'].dt.strftime("%d-%m-%Y")
        display_df = display_df.rename(columns={
            'id': 'ID', 'type': 'Tipe', 'category': 'Kategori',
            'amount': 'Jumlah', 'date': 'Tanggal', 'note': 'Catatan'
        })
        st.dataframe(display_df[['Tanggal', 'Tipe', 'Kategori', 'Jumlah', 'Catatan']],
                     use_container_width=True, hide_index=True)
        total_in = df_filtered[df_filtered['type'] == 'Pemasukan']['amount'].sum()
        total_out = df_filtered[df_filtered['type'] == 'Pengeluaran']['amount'].sum()
        col1, col2 = st.columns(2)
        col1.metric("Total Pemasukan", f"Rp {total_in:,.0f}")
        col2.metric("Total Pengeluaran", f"Rp {total_out:,.0f}")
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtered.to_excel(writer, index=False, sheet_name='Riwayat')
        st.download_button(
            label="📥 Download Laporan (Excel)",
            data=buffer.getvalue(),
            file_name=f"neraca_kehidupan_{selected_month}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )