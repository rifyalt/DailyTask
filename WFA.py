import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import plotly.graph_objects as go
import re

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Daily Task Tracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #f4f5f7;
    --surface:   #ffffff;
    --border:    #e4e6ea;
    --accent:    #2563eb;
    --accent-lt: #eff6ff;
    --ok:        #16a34a;
    --ok-lt:     #f0fdf4;
    --warn:      #d97706;
    --warn-lt:   #fffbeb;
    --danger:    #dc2626;
    --danger-lt: #fef2f2;
    --text:      #1a1d23;
    --muted:     #6b7280;
    --faint:     #adb5bd;
    --radius:    10px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.8rem !important; padding-bottom: 2rem !important; max-width: 1080px !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1.2rem !important; }

.app-brand {
    display: flex; align-items: center; gap: 11px;
    background: var(--accent-lt); border: 1px solid #bfdbfe;
    border-radius: var(--radius); padding: 13px 15px; margin-bottom: 18px;
}
.app-brand-icon {
    width: 38px; height: 38px; background: var(--accent);
    border-radius: 9px; display: flex; align-items: center;
    justify-content: center; font-size: 19px; flex-shrink: 0;
}
.app-brand-name { font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.2; }
.app-brand-sub  { font-size: 11px; color: var(--muted); }

.sb-section { font-size: 9px; font-weight: 600; letter-spacing: 1.1px;
    text-transform: uppercase; color: var(--faint); padding: 0 4px 5px; margin-top: 6px; }

.mini-card {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 11px 13px; margin-bottom: 7px;
}
.mini-card .mc-lbl { font-size: 9px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .7px; color: var(--muted); margin-bottom: 3px; }
.mini-card .mc-val { font-size: 21px; font-weight: 600; color: var(--text); }
.mini-card .mc-sub { font-size: 10px; color: var(--faint); margin-top: 1px; }
.mini-card.ok    { background: var(--ok-lt);     border-color: #bbf7d0; }
.mini-card.ok    .mc-val { color: var(--ok); }
.mini-card.danger{ background: var(--danger-lt); border-color: #fecaca; }
.mini-card.danger .mc-val { color: var(--danger); }

/* ── INPUTS ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stDateInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.08) !important;
    outline: none !important;
}
label[data-testid="stWidgetLabel"] > div > p,
.stDateInput label, .stSelectbox label,
.stTextInput label, .stNumberInput label, .stTextArea label {
    color: var(--muted) !important;
    font-size: 12px !important; font-weight: 500 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--accent) !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 14px !important;
    padding: 9px 20px !important; transition: opacity .15s !important;
    width: 100% !important;
}
.stButton > button:hover { opacity: .88 !important; }
.stFormSubmitButton > button {
    width: 100% !important; padding: 13px !important;
    font-size: 15px !important; font-weight: 600 !important;
    background: var(--accent) !important; border-radius: 8px !important;
    letter-spacing: .2px !important;
}
.stFormSubmitButton > button:hover { opacity: .88 !important; }

/* ── METRICS ── */
div[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important; padding: 16px 18px !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--muted) !important; font-size: 11px !important;
    font-weight: 600 !important; text-transform: uppercase !important;
    letter-spacing: .6px !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text) !important; font-size: 26px !important; font-weight: 600 !important;
}

/* ── FORM ── */
.stForm {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important; padding: 22px !important;
}

/* ── PAGE HEADER ── */
.pg-header {
    padding-bottom: 14px; border-bottom: 1px solid var(--border); margin-bottom: 22px;
}
.pg-header h1 {
    font-size: 20px !important; font-weight: 600 !important;
    color: var(--text) !important; margin: 0 0 2px !important;
}
.pg-header p { color: var(--muted); font-size: 13px; margin: 0; }

/* ── SECTION LABEL ── */
.sec-label {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .9px; color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 7px; margin: 18px 0 12px;
}

/* ── TASK CARD (timeline view) ── */
.task-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 13px 16px;
    margin-bottom: 8px; display: flex; align-items: flex-start; gap: 14px;
}
.task-time {
    font-size: 12px; font-weight: 600; color: var(--accent);
    min-width: 44px; padding-top: 2px; font-variant-numeric: tabular-nums;
}
.task-body { flex: 1; }
.task-title { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.task-meta  { font-size: 11px; color: var(--muted); }
.task-badge {
    font-size: 10px; font-weight: 600; padding: 2px 8px;
    border-radius: 20px; white-space: nowrap; align-self: flex-start;
}
.badge-done    { background: #dcfce7; color: #15803d; }
.badge-prog    { background: #dbeafe; color: #1d4ed8; }
.badge-pending { background: #fef9c3; color: #a16207; }
.badge-cancel  { background: #fee2e2; color: #dc2626; }
.badge-other   { background: #f3f4f6; color: #6b7280; }

/* ── NOTIF ── */
.notif {
    border-radius: 8px; padding: 12px 15px; margin-bottom: 18px;
    display: flex; align-items: flex-start; gap: 10px; border: 1px solid;
}
.notif.danger  { background: var(--danger-lt); border-color: #fecaca; }
.notif.ok      { background: var(--ok-lt);     border-color: #bbf7d0; }
.notif .ni     { font-size: 16px; line-height: 1.4; flex-shrink: 0; }
.notif .nb     { flex: 1; }
.notif .nt     { font-size: 13px; font-weight: 600; margin-bottom: 2px; }
.notif.danger .nt { color: var(--danger); }
.notif.ok     .nt { color: var(--ok); }
.notif .nd    { font-size: 12px; color: var(--muted); margin-bottom: 7px; }
.pills        { display: flex; flex-wrap: wrap; gap: 5px; }
.pill {
    font-size: 11px; font-weight: 500; padding: 2px 9px;
    border-radius: 20px; background: #fee2e2; color: var(--danger);
    border: 1px solid #fecaca;
}

/* ── PASSWORD GATE ── */
.pw-gate {
    max-width: 360px; margin: 60px auto 0; text-align: center;
}
.pw-gate .pw-icon { font-size: 40px; margin-bottom: 14px; }
.pw-gate h2 { font-size: 18px; font-weight: 600; margin-bottom: 6px; }
.pw-gate p  { font-size: 13px; color: var(--muted); margin-bottom: 22px; }

/* ── TIMELINE HOUR BLOCK ── */
.hour-block {
    display: flex; gap: 12px; margin-bottom: 4px;
    align-items: flex-start; padding: 6px 0;
    border-bottom: 1px solid var(--border);
}
.hour-label {
    font-size: 11px; font-weight: 600; color: var(--faint);
    min-width: 42px; padding-top: 3px; font-variant-numeric: tabular-nums;
}
.hour-tasks { flex: 1; display: flex; flex-wrap: wrap; gap: 5px; }
.hour-empty { font-size: 11px; color: var(--faint); padding-top: 3px; font-style: italic; }

/* ── DATAFRAME ── */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px !important; }
.stDataFrame iframe { border-radius: 8px !important; }

/* ── MISC ── */
hr { border-color: var(--border) !important; margin: 18px 0 !important; }
.stSuccess { background: var(--ok-lt) !important; border: 1px solid #bbf7d0 !important; border-radius: 8px !important; }
.stWarning { background: var(--warn-lt) !important; border: 1px solid #fde68a !important; border-radius: 8px !important; }
.stError   { background: var(--danger-lt) !important; border: 1px solid #fecaca !important; border-radius: 8px !important; }
.stDownloadButton > button {
    background: var(--bg) !important; color: var(--accent) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    font-weight: 500 !important; font-size: 13px !important; width: auto !important;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GOOGLE SHEETS
# ─────────────────────────────────────────────
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
client  = gspread.authorize(creds)
SHEET_ID = "1PvdyLJ3DRVHnd2zScnTICOSaX1pYNxzYjZ_g9ktui9o"
sheet    = client.open_by_key(SHEET_ID).sheet1

HEADERS = [
    "Date","Hour","Staff","Division","Category","Detail",
    "Booking ID","Hotel","Supplier","Quantity",
    "Status","Total Komunikasi","Detail Komunikasi","Notes","Timestamp"
]
existing = sheet.row_values(1)
if existing != HEADERS:
    sheet.clear()
    sheet.insert_row(HEADERS, 1)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
ALL_STAFF = sorted([
    "Vial","Fandi","Geraldi","Riega","Farras","Baldy",
    "Vero","Yati","Ade","Selvy","Firda","Meiji"
])

WORK_HOURS = [f"{h:02d}:00" for h in range(0, 25)]  # 00:00–24:00

CATEGORY_LIST = [
    "Booking","Voucher Issued","Follow Up Hotel","Follow Up Supplier",
    "Void","Refund","Rename Guest","Takeover Payment",
    "Inject Debit DTM","Complaint Handling","Rekap Tagihan",
]
DETAIL_LIST = sorted([
    "New Hotel Booking","Booking Amendment","Booking Cancellation","Booking Confirmation",
    "Voucher Issued","Voucher Resend","Voucher Correction",
    "Follow Up Hotel","Follow Up Supplier","Follow Up Guest",
    "Special Request Handling","Room Request Handling",
    "Rename Guest","Add Guest Name","Takeover Payment Process","Credit Card Charge",
    "Inject Debit DTM","Refund Process","Void Transaction","Dispute Handling",
    "Complaint Handling","Rate Checking","Supplier Price Verification",
    "Manual Booking","Direct Hotel Booking","Data Correction","Other"
])
STATUS_LIST = [
    "Done","In Progress","Pending",
    "Waiting Hotel Confirmation","Waiting Supplier Confirmation","Waiting Guest Response",
    "On Hold","Refund Process","Void Process","Cancelled","Escalated","Rejected"
]
SUPPLIER_LIST = ["DOTW","WebBeds","MG Holiday","Kliknbook","Direct Hotel"]

MANAGER_PASSWORD = "789789"

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "dashboard_unlocked" not in st.session_state:
    st.session_state.dashboard_unlocked = False
if "pw_error" not in st.session_state:
    st.session_state.pw_error = False

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    data = sheet.get_all_records()
    df   = pd.DataFrame(data)
    return df

def get_absent_staff(df, target_date=None):
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
    if df.empty or "Staff" not in df.columns or "Date" not in df.columns:
        return ALL_STAFF, target_date
    present = df[df["Date"] == target_date]["Staff"].unique().tolist()
    return [s for s in ALL_STAFF if s not in present], target_date

def badge_class(status):
    s = str(status).lower()
    if s == "done":       return "badge-done"
    if "progress" in s:   return "badge-prog"
    if "pending" in s or "waiting" in s or "hold" in s: return "badge-pending"
    if "cancel" in s or "reject" in s: return "badge-cancel"
    return "badge-other"

def parse_kom(s):
    """Parse komunikasi detail — new format: 'Email, WhatsApp' or old 'Email:N WA:N Telp:N'"""
    s = str(s)
    # new format: comma-separated channel names
    if ":" not in s:
        channels = [c.strip() for c in s.split(",") if c.strip() and c.strip() != "-"]
        email = sum(1 for c in channels if "Email" in c)
        wa    = sum(1 for c in channels if "WhatsApp" in c or "WA" in c)
        telp  = sum(1 for c in channels if "Telepon" in c or "Telp" in c)
        return email, wa, telp
    # legacy format: Email:N WA:N Telp:N
    try:
        e = int(re.search(r'Email:(\d+)', s).group(1))
        w = int(re.search(r'WA:(\d+)',    s).group(1))
        t = int(re.search(r'Telp:(\d+)',  s).group(1))
        return e, w, t
    except:
        return 0, 0, 0

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="app-brand">
        <div class="app-brand-icon">📋</div>
        <div>
            <div class="app-brand-name">Daily Task Tracker</div>
            <div class="app-brand-sub">Hotel Reservation Team</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Menu</div>', unsafe_allow_html=True)
    menu = st.selectbox("Menu", ["✏️  Input Task", "📊  Manager Dashboard"],
                        label_visibility="collapsed")

    st.markdown("---")
    if st.button("🔄  Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")

    # quick stats
    absent_list, chk_date = get_absent_staff(df)
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_df  = df[df["Date"] == today_str] if not df.empty and "Date" in df.columns else pd.DataFrame()
    absent_cls = "danger" if absent_list else "ok"

    st.markdown('<div class="sb-section">Hari Ini</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mini-card">
        <div class="mc-lbl">Total Task</div>
        <div class="mc-val">{len(today_df)}</div>
        <div class="mc-sub">{today_str}</div>
    </div>
    <div class="mini-card {absent_cls}">
        <div class="mc-lbl">Belum Input</div>
        <div class="mc-val">{len(absent_list)}</div>
        <div class="mc-sub">dari {len(ALL_STAFF)} staff</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PAGE: INPUT TASK
# ═══════════════════════════════════════════════
if "Input" in menu:

    st.markdown("""
    <div class="pg-header">
        <h1>✏️ Input Task Harian</h1>
        <p>Catat setiap task yang dikerjakan beserta jam mulainya.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── My Tasks Today (per staff) ─────────────────
    # Staff selector outside form so we can show their timeline
    sel_staff = st.selectbox("☺️ Pilih nama Anda", ALL_STAFF, key="staff_selector")

    # Show today's timeline for selected staff
    my_tasks = today_df[today_df["Staff"] == sel_staff] if not today_df.empty and "Staff" in today_df.columns else pd.DataFrame()

    if not my_tasks.empty:
        st.markdown('<div class="sec-label">Timeline Anda Hari Ini</div>', unsafe_allow_html=True)
        for _, row in my_tasks.sort_values("Hour").iterrows():
            cat   = row.get("Category","")
            det   = row.get("Detail","")
            stat  = row.get("Status","")
            hotel = row.get("Hotel","")
            bid   = row.get("Booking ID","")
            hour  = row.get("Hour","--:--")
            bc    = badge_class(stat)
            meta_parts = [x for x in [hotel, bid] if x]
            meta = " · ".join(meta_parts) if meta_parts else cat
            st.markdown(f"""
            <div class="task-card">
                <div class="task-time">{hour}</div>
                <div class="task-body">
                    <div class="task-title">{cat} — {det}</div>
                    <div class="task-meta">{meta}</div>
                </div>
                <div class="task-badge {bc}">{stat}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Tambah Task Baru</div>', unsafe_allow_html=True)

    with st.form("task_form", clear_on_submit=True):

        # Row 1: tanggal + jam + divisi
        r1a, r1b, r1c = st.columns(3)
        with r1a:
            task_date = st.date_input("📅 Tanggal", value=date.today())
        with r1b:
            _now_hour = datetime.now().hour
            _default_idx = min(_now_hour, len(WORK_HOURS) - 1)
            task_hour = st.selectbox("🕐 Jam Mulai", WORK_HOURS, index=_default_idx)
        with r1c:
            division = st.selectbox("🏢 Divisi", [
                "Hotel Reservation","Admin Reservation","Finance"
            ])

        # Row 2: kategori + detail
        r2a, r2b = st.columns(2)
        with r2a:
            category = st.selectbox("#️⃣ Kategori", CATEGORY_LIST)
        with r2b:
            detail = st.selectbox("🆕 Detail Aktivitas", DETAIL_LIST)

        # Row 3: booking info
        r3a, r3b, r3c = st.columns(3)
        with r3a:
            booking_id = st.text_input("ℹ️ Booking ID", placeholder="e.g. VAGHB2603842454")
        with r3b:
            hotel = st.text_input("🛅 Hotel", placeholder="e.g. Grand Hyatt Jakarta")
        with r3c:
            supplier = st.selectbox("🛄 Supplier", SUPPLIER_LIST)

        # Row 4: qty + status
        r4a, r4b = st.columns(2)
        with r4a:
            qty = st.number_input("🔢 Qty", min_value=1, value=1)
        with r4b:
            status = st.selectbox("*️⃣ Status", STATUS_LIST)

        # Komunikasi — multiselect checkboxes
        st.markdown("<div style='font-size:12px;font-weight:500;color:#6b7280;margin-bottom:4px;'>Jalur Komunikasi</div>", unsafe_allow_html=True)
        kom_channels = st.multiselect(
            "Jalur Komunikasi",
            options=["1️⃣ Email", "2️⃣ WhatsApp", "3️⃣ Telepon"],
            default=[],
            label_visibility="collapsed",
            placeholder="Pilih jalur komunikasi yang digunakan..."
        )

        # Timezone selector
        TIMEZONE_OPTIONS = {
            "WIB — Jakarta, Indonesia (UTC+7)":         "Asia/Jakarta",
            "WITA — Makassar, Indonesia (UTC+8)":       "Asia/Makassar",
            "WIT — Jayapura, Indonesia (UTC+9)":        "Asia/Jayapura",
            "MYT — Kuala Lumpur, Malaysia (UTC+8)":     "Asia/Kuala_Lumpur",
            "SGT — Singapura (UTC+8)":                  "Asia/Singapore",
            "THA — Bangkok, Thailand (UTC+7)":          "Asia/Bangkok",
        }
        tz_label = st.selectbox(
            "🌏 Zona Waktu",
            options=list(TIMEZONE_OPTIONS.keys()),
            index=0
        )

        # Notes
        notes = st.text_area("📝 Catatan", placeholder="Opsional — isi jika ada hal penting...", height=80)

        submitted = st.form_submit_button("✅  Simpan Task", use_container_width=True)

        if submitted:
            import pytz
            tz_name   = TIMEZONE_OPTIONS[tz_label]
            tz_obj    = pytz.timezone(tz_name)
            now_local = datetime.now(tz_obj)
            tz_abbr   = tz_label.split(" — ")[0]   # e.g. "WIB"
            ts = now_local.strftime(f"%Y-%m-%d %H:%M:%S") + f" {tz_abbr}"

            kom_detail = ", ".join([c.split(" ", 1)[1] for c in kom_channels]) if kom_channels else "-"
            kom_total  = len(kom_channels)
            new_row = [
                str(task_date), task_hour, sel_staff, division,
                category, detail, booking_id, hotel, supplier,
                qty, status, kom_total, kom_detail, notes,
                ts
            ]
            sheet.append_row(new_row)
            st.cache_data.clear()
            st.success(f"✅ Task **{task_hour} — {category}** berhasil disimpan!")
            st.rerun()

# ═══════════════════════════════════════════════
# PAGE: MANAGER DASHBOARD (password gated)
# ═══════════════════════════════════════════════
if "Dashboard" in menu:

    # ── PASSWORD GATE ──────────────────────────────
    if not st.session_state.dashboard_unlocked:
        st.markdown("""
        <div class="pg-header">
            <h1>📊 Manager Dashboard</h1>
            <p>Halaman ini membutuhkan autentikasi.</p>
        </div>
        """, unsafe_allow_html=True)

        col_c = st.columns([1, 2, 1])[1]
        with col_c:
            st.markdown("""
            <div style="background:var(--surface);border:1px solid var(--border);
                        border-radius:14px;padding:32px 28px;text-align:center;margin-top:20px;">
                <div style="font-size:36px;margin-bottom:12px;">🔒</div>
                <div style="font-size:17px;font-weight:600;margin-bottom:6px;">Manager Only</div>
                <div style="font-size:13px;color:var(--muted);margin-bottom:22px;">
                    Masukkan password untuk mengakses dashboard.
                </div>
            </div>
            """, unsafe_allow_html=True)
            pw_input = st.text_input("Password", type="password",
                                     placeholder="Masukkan password...",
                                     label_visibility="collapsed")
            if st.button("🔓  Masuk", use_container_width=True):
                if pw_input == MANAGER_PASSWORD:
                    st.session_state.dashboard_unlocked = True
                    st.session_state.pw_error = False
                    st.rerun()
                else:
                    st.session_state.pw_error = True
                    st.rerun()
            if st.session_state.pw_error:
                st.error("❌ Password salah. Silakan coba lagi.")
        st.stop()

    # ── DASHBOARD CONTENT ──────────────────────────
    header_c, logout_c = st.columns([5, 1])
    with header_c:
        st.markdown("""
        <div class="pg-header">
            <h1>📊 Manager Dashboard</h1>
            <p>Pantau aktivitas tim reservasi secara real-time.</p>
        </div>
        """, unsafe_allow_html=True)
    with logout_c:
        st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
        if st.button("🔒 Keluar", use_container_width=True):
            st.session_state.dashboard_unlocked = False
            st.rerun()

    # ── Absent Notification ────────────────────────
    absent_list, chk_date = get_absent_staff(df)
    if absent_list:
        pills = "".join([f'<span class="pill">{s}</span>' for s in absent_list])
        st.markdown(f"""
        <div class="notif danger">
            <div class="ni">🔔</div>
            <div class="nb">
                <div class="nt">{len(absent_list)} staff belum input hari ini
                    <span style="font-size:11px;font-weight:400;color:var(--muted);margin-left:6px;">{chk_date}</span>
                </div>
                <div class="nd">Silakan ingatkan staff berikut.</div>
                <div class="pills">{pills}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="notif ok">
            <div class="ni">✅</div>
            <div class="nb">
                <div class="nt">Semua staff sudah input!</div>
                <div class="nd" style="margin-bottom:0">
                    Seluruh {len(ALL_STAFF)} staff telah mencatat aktivitas hari ini ({chk_date}).
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if df.empty:
        st.warning("⚠️ Belum ada data. Silakan input aktivitas terlebih dahulu.")
        st.stop()

    # ── Date filter ────────────────────────────────
    st.markdown('<div class="sec-label">Filter Tampilan</div>', unsafe_allow_html=True)
    fa, fb, fc, _ = st.columns([2,2,2,4])
    with fa:
        sel_date_filter = st.selectbox("Periode", ["Hari Ini","7 Hari Terakhir","Semua"])
    with fb:
        sel_staff_filter = st.selectbox("Staff",
            ["Semua"] + ALL_STAFF)
    with fc:
        sel_div_filter = st.selectbox("Divisi",
            ["Semua","Hotel Reservation","Admin Reservation","Finance"])

    fdf = df.copy()
    if "Date" in fdf.columns:
        fdf["Date"] = fdf["Date"].astype(str)
        today_str = datetime.now().strftime("%Y-%m-%d")
        if sel_date_filter == "Hari Ini":
            fdf = fdf[fdf["Date"] == today_str]
        elif sel_date_filter == "7 Hari Terakhir":
            fdf["_d"] = pd.to_datetime(fdf["Date"], errors="coerce")
            fdf = fdf[fdf["_d"] >= pd.Timestamp.now() - pd.Timedelta(days=7)].drop(columns="_d")
    if sel_staff_filter != "Semua" and "Staff" in fdf.columns:
        fdf = fdf[fdf["Staff"] == sel_staff_filter]
    if sel_div_filter != "Semua" and "Division" in fdf.columns:
        fdf = fdf[fdf["Division"] == sel_div_filter]

    # ── KPIs ───────────────────────────────────────
    st.markdown('<div class="sec-label">Ringkasan</div>', unsafe_allow_html=True)
    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.metric("📋 Total Task", len(fdf))
    with k2: st.metric("👥 Aktif Staff", fdf["Staff"].nunique() if "Staff" in fdf.columns else 0)
    with k3: st.metric("🔢 Total Qty",   int(fdf["Quantity"].sum()) if "Quantity" in fdf.columns else 0)
    with k4:
        done = len(fdf[fdf["Status"]=="Done"]) if "Status" in fdf.columns else 0
        st.metric("✅ Done", done)
    with k5:
        total_kom = int(fdf["Total Komunikasi"].sum()) if "Total Komunikasi" in fdf.columns else 0
        st.metric("💬 Komunikasi", total_kom)

    st.divider()

    # ── Hourly Activity Heatmap (today or filtered) ─
    st.markdown('<div class="sec-label">Aktivitas per Jam</div>', unsafe_allow_html=True)
    if "Hour" in fdf.columns and not fdf.empty:
        hour_counts = fdf.groupby("Hour").size().reset_index(name="n")
        all_hours_df = pd.DataFrame({"Hour": WORK_HOURS})
        hour_counts = all_hours_df.merge(hour_counts, on="Hour", how="left").fillna(0)
        hour_counts["n"] = hour_counts["n"].astype(int)

        fig_h = go.Figure(go.Bar(
            x=hour_counts["Hour"],
            y=hour_counts["n"],
            marker=dict(
                color=hour_counts["n"],
                colorscale=[[0,"#e0e7ff"],[0.4,"#93c5fd"],[1,"#2563eb"]],
                line=dict(width=0)
            ),
            text=hour_counts["n"].apply(lambda v: str(v) if v > 0 else ""),
            textposition="outside",
            textfont=dict(color="#6b7280", size=12)
        ))
        fig_h.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#6b7280", family="DM Sans"),
            margin=dict(l=0,r=0,t=8,b=0), height=200,
            xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#374151")),
            yaxis=dict(showgrid=True, gridcolor="#f3f4f6", showticklabels=False, zeroline=False),
            bargap=0.25,
        )
        st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})

    # ── Charts row ─────────────────────────────────
    ca, cb = st.columns([3,2])
    with ca:
        st.markdown('<div class="sec-label">Task per Staff</div>', unsafe_allow_html=True)
        if "Staff" in fdf.columns and not fdf.empty:
            sc = fdf.groupby("Staff").size().reset_index(name="n").sort_values("n")
            fig_s = go.Figure(go.Bar(
                x=sc["n"], y=sc["Staff"], orientation="h",
                marker=dict(color="#2563eb", line=dict(width=0)),
                text=sc["n"], textposition="outside",
                textfont=dict(color="#6b7280", size=12)
            ))
            fig_s.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6b7280", family="DM Sans"),
                margin=dict(l=0,r=36,t=8,b=0), height=320,
                xaxis=dict(showgrid=True, gridcolor="#f3f4f6", showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#374151")),
                bargap=0.38,
            )
            st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})

    with cb:
        st.markdown('<div class="sec-label">Kategori</div>', unsafe_allow_html=True)
        if "Category" in fdf.columns and not fdf.empty:
            cc = fdf.groupby("Category").size().reset_index(name="n")
            colors = ["#2563eb","#0891b2","#16a34a","#d97706","#dc2626",
                      "#7c3aed","#0d9488","#9333ea","#ea580c","#65a30d","#be185d"]
            fig_c = go.Figure(go.Pie(
                labels=cc["Category"], values=cc["n"], hole=0.52,
                marker=dict(colors=colors[:len(cc)], line=dict(color="#fff",width=2)),
                textinfo="percent",
                textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{label}</b><br>%{value} task<br>%{percent}<extra></extra>"
            ))
            fig_c.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6b7280", family="DM Sans"),
                legend=dict(font=dict(size=10, color="#6b7280"), bgcolor="rgba(0,0,0,0)",
                            orientation="h", x=0, y=-0.18),
                margin=dict(l=0,r=0,t=8,b=60), height=320,
                annotations=[dict(
                    text=f"<b>{len(fdf)}</b><br><span style='font-size:10px'>tasks</span>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=15, color="#1a1d23", family="DM Sans")
                )]
            )
            st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})

    # ── Row 2 charts ───────────────────────────────
    cd, ce = st.columns(2)
    with cd:
        st.markdown('<div class="sec-label">Supplier</div>', unsafe_allow_html=True)
        if "Supplier" in fdf.columns and not fdf.empty:
            sp = fdf.groupby("Supplier").size().reset_index(name="n").sort_values("n", ascending=False)
            fig_sp = go.Figure(go.Bar(
                x=sp["Supplier"], y=sp["n"],
                marker=dict(color="#0891b2", line=dict(width=0)),
                text=sp["n"], textposition="outside",
                textfont=dict(color="#6b7280", size=13)
            ))
            fig_sp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6b7280", family="DM Sans"),
                margin=dict(l=0,r=0,t=8,b=0), height=240,
                xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#374151")),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6", showticklabels=False, zeroline=False),
                bargap=0.42,
            )
            st.plotly_chart(fig_sp, use_container_width=True, config={"displayModeBar": False})

    with ce:
        st.markdown('<div class="sec-label">Komunikasi per Channel</div>', unsafe_allow_html=True)
        if "Detail Komunikasi" in fdf.columns and not fdf.empty:
            parsed   = fdf["Detail Komunikasi"].apply(parse_kom)
            t_email  = sum(x[0] for x in parsed)
            t_wa     = sum(x[1] for x in parsed)
            t_telp   = sum(x[2] for x in parsed)
            fig_k = go.Figure(go.Bar(
                x=["Email","WhatsApp","Telepon"],
                y=[t_email, t_wa, t_telp],
                marker=dict(color=["#2563eb","#16a34a","#d97706"], line=dict(width=0)),
                text=[t_email, t_wa, t_telp], textposition="outside",
                textfont=dict(color="#6b7280", size=13)
            ))
            fig_k.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6b7280", family="DM Sans"),
                margin=dict(l=0,r=0,t=8,b=0), height=240,
                xaxis=dict(showgrid=False, tickfont=dict(size=13, color="#374151")),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6", showticklabels=False, zeroline=False),
                bargap=0.45,
            )
            st.plotly_chart(fig_k, use_container_width=True, config={"displayModeBar": False})

    # ── Tren harian ────────────────────────────────
    if "Date" in fdf.columns and fdf["Date"].nunique() > 1:
        st.markdown('<div class="sec-label">Tren Harian</div>', unsafe_allow_html=True)
        daily = fdf.groupby("Date").size().reset_index(name="n")
        daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
        daily = daily.dropna().sort_values("Date")
        fig_t = go.Figure(go.Scatter(
            x=daily["Date"], y=daily["n"],
            mode="lines+markers",
            line=dict(color="#2563eb", width=2),
            marker=dict(size=6, color="#2563eb", line=dict(color="white", width=1.5)),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.06)",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y} task<extra></extra>"
        ))
        fig_t.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#6b7280", family="DM Sans"),
            margin=dict(l=0,r=0,t=8,b=0), height=200,
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#6b7280")),
            yaxis=dict(showgrid=True, gridcolor="#f3f4f6", tickfont=dict(size=11, color="#6b7280"), zeroline=False),
        )
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

    # ── Timeline detail (per-hour breakdown) ───────
    st.divider()
    st.markdown('<div class="sec-label">Timeline Detail Hari Ini per Staff</div>', unsafe_allow_html=True)
    today_all = df[df["Date"] == today_str] if not df.empty and "Date" in df.columns else pd.DataFrame()
    if today_all.empty:
        st.info("Belum ada task yang diinput hari ini.")
    else:
        for staff_name in ALL_STAFF:
            staff_tasks = today_all[today_all["Staff"] == staff_name] if "Staff" in today_all.columns else pd.DataFrame()
            if staff_tasks.empty:
                continue
            with st.expander(f"👤 {staff_name}  ({len(staff_tasks)} task)", expanded=False):
                for _, row in staff_tasks.sort_values("Hour").iterrows():
                    cat   = row.get("Category","")
                    det   = row.get("Detail","")
                    stat  = row.get("Status","")
                    hotel = row.get("Hotel","")
                    bid   = row.get("Booking ID","")
                    hour  = row.get("Hour","--:--")
                    notes = row.get("Notes","")
                    bc    = badge_class(stat)
                    meta_parts = [x for x in [hotel, bid] if x]
                    meta = " · ".join(meta_parts) if meta_parts else ""
                    st.markdown(f"""
                    <div class="task-card">
                        <div class="task-time">{hour}</div>
                        <div class="task-body">
                            <div class="task-title">{cat} — {det}</div>
                            <div class="task-meta">{meta}{' · ' + notes if notes else ''}</div>
                        </div>
                        <div class="task-badge {bc}">{stat}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Data Table ─────────────────────────────────
    st.divider()
    st.markdown('<div class="sec-label">Tabel Data Lengkap</div>', unsafe_allow_html=True)
    st.dataframe(fdf, use_container_width=True, height=360, hide_index=True)

    dl1, _ = st.columns([1,5])
    with dl1:
        csv = fdf.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "task_report.csv", mime="text/csv")
