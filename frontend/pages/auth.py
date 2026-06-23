import os
import time
import json
import hashlib
import html
import streamlit as st
# =========================
# LANDING & LOGIN CONFIG
# =========================
CAMPUS_LOGO_PATH = "assets/logo itsb.jpeg"
TEAM_MEMBERS = [
    {
        "name": "Ulin Nikmah",
        "nim": "52250042",
        "username": "ulin",
        "email": "ulin@example.com",
        "password": "52250042",
        "photo": "assets/ulin.jpeg",
        "role": "Anggota Kelompok 7",
        "focus": "UI/UX & Styling",
        "contribution": "Membantu pengembangan dashboard Auto EDA, analisis data, dan persiapan presentasi."
    },
    {
        "name": "Paskalis Farelnata Zamasi",
        "nim": "52250043",
        "username": "paskalis",
        "email": "paskalis@example.com",
        "password": "52250043",
        "photo": "assets/paskalis.png",
        "role": "Anggota Kelompok 7",
        "focus": "Dashboard Integration",
        "contribution": "Membantu integrasi dashboard, pengujian fitur, UI/UX, dan finalisasi project."
    },
    {
        "name": "Nazwa Nur Ramadhani",
        "nim": "52250045",
        "username": "nazwa",
        "email": "nazwa@example.com",
        "password": "52250045",
        "photo": "assets/nazwa.png",
        "role": "Anggota Kelompok 7",
        "focus": "Statistics & Insight",
        "contribution": "Membantu statistik deskriptif, visualisasi, dan pengecekan hasil analisis."
    },
    {
        "name": "Veronica Maria L F Xavier",
        "nim": "52250021",
        "username": "veronica",
        "email": "veronica@example.com",
        "password": "52250021",
        "photo": "assets/veronica.jpeg",
        "role": "Anggota Kelompok 7",
        "focus": "Reporting & Documentation",
        "contribution": "Membantu dokumentasi, pelaporan, dan evaluasi tampilan dashboard."
    }
]
INFO_ITEMS = [
    {
        "modal_id": "modal_matkul",
        "icon": "📚",
        "label": "Mata Kuliah",
        "value": "Data Science Programming",
        "description": "Mata kuliah ini berfokus pada penerapan pemrograman untuk analisis data, EDA, visualisasi, dan pengembangan dashboard interaktif."
    },
    {
        "modal_id": "modal_dosen",
        "icon": "👨‍🏫",
        "label": "Dosen Pengampu",
        "value": "Bakti Siregar, M.Sc., CDS.",
        "description": "Beliau merupakan dosen pengampu mata kuliah Data Science Programming yang membimbing pengembangan mini project dashboard EDA ini."
    },
    {
        "modal_id": "modal_prodi",
        "icon": "🎓",
        "label": "Program Studi",
        "value": "Sains Data",
        "description": "Program Studi Sains Data berfokus pada analisis data, machine learning, visualisasi, serta pengambilan keputusan berbasis data."
    }
]
LOGIN_USERS = TEAM_MEMBERS + [
    {
        "name": "Mr. Bakti",
        "nim": "-",
        "username": "Mr. Bakti",
        "email": "mrbakti@example.com",
        "password": "11111111",
        "photo": ""
    }
]
REGISTERED_USERS_PATH = "data/registered_users.json"
# =========================
# HELPER
# =========================
def get_file_data_uri(file_path):
    import base64
    import mimetypes
    if not file_path or not os.path.exists(file_path):
        return None
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "image/png"
    with open(file_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"
def inject_click_profile_css():
    st.markdown(
        """
        <style>
            .profile-link-card {
                display: block !important;
                text-decoration: none !important;
                color: inherit !important;
            }
            .profile-link-card:hover {
                text-decoration: none !important;
                color: inherit !important;
            }
            .profile-link-card .member-card,
            .profile-link-card .identity-item {
                cursor: pointer !important;
                transition: all 0.25s ease !important;
            }
            .profile-link-card .member-card:hover,
            .profile-link-card .identity-item:hover {
                transform: translateY(-6px) scale(1.025) !important;
                border-color: rgba(56, 189, 248, 0.55) !important;
                box-shadow:
                    0 22px 56px rgba(0,0,0,.34),
                    0 0 32px rgba(34, 211, 238, .13) !important;
            }
            .profile-modal-backdrop {
                position: fixed;
                inset: 0;
                z-index: 999999;
                display: none;
                justify-content: center;
                align-items: flex-start;
                padding: 7vh 24px 24px;
                background: rgba(2, 6, 23, 0.78);
                backdrop-filter: blur(12px);
            }
            .profile-modal-backdrop:target {
                display: flex;
            }
            .profile-modal-card {
                width: min(860px, 94vw);
                min-height: 300px;
                display: flex;
                align-items: center;
                gap: 28px;
                padding: 30px;
                border-radius: 34px;
                background:
                    radial-gradient(circle at 8% 0%, rgba(45, 212, 191, 0.22), transparent 34%),
                    radial-gradient(circle at 100% 0%, rgba(244, 114, 182, 0.18), transparent 34%),
                    linear-gradient(135deg, #071d3f, #0c214f);
                border: 1px solid rgba(125, 211, 252, 0.34);
                box-shadow: 0 30px 95px rgba(0,0,0,.48);
                position: relative;
                animation: profileZoomIn .24s ease;
            }
            @keyframes profileZoomIn {
                from {
                    opacity: 0;
                    transform: translateY(16px) scale(.94);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            .profile-modal-close {
                position: absolute;
                top: 16px;
                right: 16px;
                width: 38px;
                height: 38px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                border: 1px solid rgba(255,255,255,.18);
                background: rgba(255,255,255,.08);
                color: white !important;
                text-decoration: none !important;
                font-weight: 950;
                font-size: 24px;
                line-height: 1;
            }
            .profile-modal-photo {
                width: 190px;
                height: 190px;
                border-radius: 50%;
                object-fit: cover;
                border: 4px solid rgba(186,230,253,.94);
                box-shadow: 0 0 34px rgba(56,189,248,.26);
                flex-shrink: 0;
            }
            .profile-modal-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(255,255,255,.08);
                font-size: 68px;
            }
            .profile-modal-right {
                flex: 1;
                min-width: 0;
            }
            .profile-modal-title {
                font-size: clamp(29px, 4vw, 44px);
                line-height: 1.05;
                font-weight: 950;
                background: linear-gradient(90deg, #5eead4, #f472b6, #7dd3fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            .profile-modal-subtitle {
                color: #bae6fd;
                font-weight: 900;
                letter-spacing: .02em;
                margin-bottom: 14px;
            }
            .profile-modal-desc {
                color: inherit;
                line-height: 1.7;
                background: rgba(255,255,255,.06);
                border: 1px solid rgba(255,255,255,.08);
                padding: 15px 17px;
                border-radius: 18px;
                font-size: 15px;
            }
            /* Auto highlight card yang sedang dipilih */
            body:has(#member_0:target) a[href="#member_0"] .member-card,
            body:has(#member_1:target) a[href="#member_1"] .member-card,
            body:has(#member_2:target) a[href="#member_2"] .member-card,
            body:has(#member_3:target) a[href="#member_3"] .member-card,
            body:has(#modal_matkul:target) a[href="#modal_matkul"] .identity-item,
            body:has(#modal_dosen:target) a[href="#modal_dosen"] .identity-item,
            body:has(#modal_prodi:target) a[href="#modal_prodi"] .identity-item {
                border-color: rgba(34, 211, 238, 0.95) !important;
                box-shadow:
                    0 0 0 2px rgba(34, 211, 238, 0.38),
                    0 0 28px rgba(34, 211, 238, 0.28),
                    0 20px 52px rgba(0,0,0,.38) !important;
                transform: translateY(-5px) scale(1.022) !important;
            }
            .profile-modal-actions {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin-top: 15px;
            }
            .profile-modal-nav {
                flex: 1;
                min-width: 150px;
                text-align: center;
                padding: 10px 14px;
                border-radius: 999px;
                text-decoration: none !important;
                color: #67e8f9 !important;
                font-weight: 900;
                font-size: 13px;
                letter-spacing: .02em;
                background: linear-gradient(135deg, rgba(8, 145, 178, .22), rgba(88, 28, 135, .20));
                border: 1px solid rgba(34, 211, 238, .34);
                box-shadow: 0 0 18px rgba(34, 211, 238, .08);
                transition: .22s ease;
            }
            .profile-modal-nav:hover {
                transform: translateY(-2px);
                background: linear-gradient(135deg, rgba(8, 145, 178, .32), rgba(88, 28, 135, .30));
                border-color: rgba(34, 211, 238, .60);
            }

            /* =========================
               AESTHETIC UPGRADE LANDING
               ========================= */

            .landing-card {
                position: relative !important;
                overflow: hidden !important;
                isolation: isolate !important;
            }

            .landing-card::before {
                content: "";
                position: absolute;
                inset: -120px;
                background:
                    radial-gradient(circle at 18% 18%, rgba(45, 212, 191, .16), transparent 24%),
                    radial-gradient(circle at 82% 16%, rgba(244, 114, 182, .13), transparent 25%),
                    radial-gradient(circle at 55% 100%, rgba(59, 130, 246, .10), transparent 30%);
                filter: blur(4px);
                z-index: -1;
                animation: landingGlowMove 8s ease-in-out infinite alternate;
            }

            @keyframes landingGlowMove {
                from {
                    transform: translate3d(-12px, -8px, 0) scale(1);
                    opacity: .72;
                }
                to {
                    transform: translate3d(14px, 10px, 0) scale(1.04);
                    opacity: 1;
                }
            }

            .project-title {
                position: relative !important;
                background-size: 220% auto !important;
                animation: titleGradientFlow 5.5s ease-in-out infinite alternate !important;
                text-shadow: 0 0 26px rgba(34, 211, 238, .10) !important;
            }

            @keyframes titleGradientFlow {
                from {
                    background-position: 0% center;
                    filter: drop-shadow(0 0 5px rgba(34, 211, 238, .06));
                }
                to {
                    background-position: 100% center;
                    filter: drop-shadow(0 0 14px rgba(244, 114, 182, .15));
                }
            }

            .project-title::after {
                content: "";
                position: absolute;
                top: -16%;
                left: -28%;
                width: 18%;
                height: 140%;
                background: linear-gradient(110deg, transparent, rgba(255,255,255,.34), transparent);
                transform: skewX(-18deg);
                animation: titleShine 4.2s ease-in-out infinite;
                opacity: .35;
                pointer-events: none;
            }

            @keyframes titleShine {
                0%, 28% {
                    left: -30%;
                    opacity: 0;
                }
                40% {
                    opacity: .42;
                }
                64%, 100% {
                    left: 112%;
                    opacity: 0;
                }
            }

            .landing-info-strip {
                width: min(760px, 92%);
                margin: 12px auto 0;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 9px;
                flex-wrap: wrap;
                padding: 9px 14px;
                border-radius: 999px;
                background: linear-gradient(135deg, rgba(8, 145, 178, .12), rgba(88, 28, 135, .14));
                border: 1px solid rgba(34, 211, 238, .18);
                color: rgba(219, 234, 254, .78);
                font-size: 12px;
                font-weight: 800;
                letter-spacing: .05em;
                text-transform: uppercase;
                box-shadow: inset 0 0 18px rgba(255,255,255,.025);
            }

            .landing-info-dot {
                width: 5px;
                height: 5px;
                border-radius: 50%;
                background: rgba(34, 211, 238, .80);
                box-shadow: 0 0 11px rgba(34, 211, 238, .55);
            }

            .profile-mini-badge {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin: 7px auto 5px;
                padding: 4px 10px;
                border-radius: 999px;
                color: inherit;
                background: linear-gradient(135deg, rgba(8, 145, 178, .16), rgba(88, 28, 135, .18));
                border: 1px solid rgba(34, 211, 238, .23);
                box-shadow: 0 0 16px rgba(34, 211, 238, .06);
                font-size: 10px;
                font-weight: 900;
                letter-spacing: .05em;
                text-transform: uppercase;
            }

            .profile-link-card .member-card:hover .profile-mini-badge {
                border-color: rgba(34, 211, 238, .52);
                background: linear-gradient(135deg, rgba(8, 145, 178, .28), rgba(88, 28, 135, .27));
                color: #a5f3fc;
            }
.profile-modal-desc b {
                color: #67e8f9;
                font-weight: 900;
            }

            div[data-testid="stButton"] > button {
                transition: all .22s ease !important;
            }

            div[data-testid="stButton"] > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 0 24px rgba(34, 211, 238, .18) !important;
                border-color: rgba(34, 211, 238, .40) !important;
            }


            /* Final spacing: strip atas dihapus, tombol login jangan terpotong */
            .landing-wrapper {
                margin-bottom: 0.55rem !important;
            }

            .identity-box {
                margin-bottom: 0.25rem !important;
            }

            div[data-testid="stButton"] > button {
                min-height: 42px !important;
                padding-top: 0.55rem !important;
                padding-bottom: 0.55rem !important;
                overflow: visible !important;
            }

            .block-container,
            div[data-testid="stMainBlockContainer"] {
                padding-bottom: 0.45rem !important;
            }

            @media (prefers-reduced-motion: reduce) {
                .landing-card::before,
                .project-title,
                .project-title::after,
                .profile-modal-card {
                    animation: none !important;
                }
            }


            /* Nama kampus dibuat berada di tengah bar atas */
            .top-campus-bar {
                position: relative !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }

            .campus-left {
                width: 100% !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 18px !important;
            }

            .campus-logo {
                position: absolute !important;
                left: 28px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
            }

            .campus-name-left {
                color: #f8fafc !important;
                font-weight: 950 !important;
                font-size: clamp(16px, 1.65vw, 24px) !important;
                letter-spacing: .12em !important;
                text-transform: uppercase !important;
                white-space: nowrap !important;
                opacity: .98 !important;
                text-align: center !important;
                text-shadow:
                    0 0 16px rgba(34, 211, 238, .20),
                    0 0 28px rgba(59, 130, 246, .12) !important;
            }

            .campus-right {
                display: none !important;
            }

            @media (max-width: 800px) {
                .campus-logo {
                    left: 16px !important;
                }

                .campus-name-left {
                    font-size: 12px !important;
                    letter-spacing: .05em !important;
                    white-space: normal !important;
                    padding-left: 82px !important;
                    padding-right: 12px !important;
                }
            }

            @media (max-width: 700px) {
                .profile-modal-card {
                    flex-direction: column;
                    text-align: center;
                }
                .profile-modal-photo {
                    width: 140px;
                    height: 140px;
                }
            }


            /* FINAL AUTH THEME FIX */
            .login-card,
            .landing-card,
            .identity-box,
            .member-card {
                color: inherit !important;
            }

            .login-subtitle,
            .project-subtitle,
            .member-nim,
            .identity-label {
                color: rgba(226, 232, 240, 0.88) !important;
            }

            .member-name,
            .identity-value {
                color: #f8fafc !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
def build_modal_html(
    modal_id,
    title,
    subtitle,
    description,
    photo_path="",
    icon="📊",
    prev_id=None,
    next_id=None
):
    photo_html = ""
    if photo_path:
        photo_uri = get_file_data_uri(photo_path)
        if photo_uri:
            photo_html = f'<img src="{photo_uri}" class="profile-modal-photo">'
    if not photo_html:
        photo_html = f'<div class="profile-modal-photo profile-modal-icon">{html.escape(icon)}</div>'
    prev_link = prev_id or modal_id
    next_link = next_id or modal_id
    return f"""
    <div id="{html.escape(modal_id)}" class="profile-modal-backdrop">
        <div class="profile-modal-card">
            <a class="profile-modal-close" href="#close" target="_self">×</a>
            <div class="profile-modal-left">
                {photo_html}
            </div>
            <div class="profile-modal-right">
                <div class="profile-modal-title">{html.escape(title)}</div>
                <div class="profile-modal-subtitle">{html.escape(subtitle)}</div>
                <div class="profile-modal-desc">{description}</div>
                <div class="profile-modal-actions">
                    <a class="profile-modal-nav" href="#{html.escape(prev_link)}" target="_self">← Profil Sebelumnya</a>
                    <a class="profile-modal-nav" href="#{html.escape(next_link)}" target="_self">Profil Berikutnya →</a>
                </div>
            </div>
        </div>
    </div>
    """
def render_all_profile_modals():
    modal_parts = []
    modal_ids = [
        "member_0",
        "member_1",
        "member_2",
        "member_3",
        "modal_matkul",
        "modal_dosen",
        "modal_prodi",
    ]
    for i, member in enumerate(TEAM_MEMBERS):
        current_id = f"member_{i}"
        current_pos = modal_ids.index(current_id)
        prev_id = modal_ids[current_pos - 1]
        next_id = modal_ids[(current_pos + 1) % len(modal_ids)]
        description = (
            f"<b>Role:</b> {html.escape(member.get('role', '-'))}<br>"
            f"<b>Username:</b> {html.escape(member.get('username', '-'))}<br>"
            f"<b>Email:</b> {html.escape(member.get('email', '-'))}<br>"
            f"<b>Kontribusi:</b> {html.escape(member.get('contribution', '-'))}"
        )
        modal_parts.append(
            build_modal_html(
                modal_id=current_id,
                title=member["name"],
                subtitle="",
                description=description,
                photo_path=member.get("photo", ""),
                icon="👤",
                prev_id=prev_id,
                next_id=next_id
            )
        )
    for item in INFO_ITEMS:
        current_id = item["modal_id"]
        current_pos = modal_ids.index(current_id)
        prev_id = modal_ids[current_pos - 1]
        next_id = modal_ids[(current_pos + 1) % len(modal_ids)]
        description = (
            f"<b>{html.escape(item['label'])}:</b> {html.escape(item['value'])}<br>"
            f"{html.escape(item['description'])}"
        )
        modal_parts.append(
            build_modal_html(
                modal_id=current_id,
                title=item["value"],
                subtitle=item["label"],
                description=description,
                photo_path="",
                icon=item["icon"],
                prev_id=prev_id,
                next_id=next_id
            )
        )
    st.markdown("\n".join(modal_parts), unsafe_allow_html=True)
def render_member_card(member, index):
    photo_uri = get_file_data_uri(member.get("photo"))
    initials = "".join([name[0] for name in member["name"].split()[:2]]).upper()
    if photo_uri:
        photo_html = f'<img src="{photo_uri}" class="member-photo">'
    else:
        photo_html = f"""
        <div class="member-photo" style="
            margin:0 auto;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#dbeafe;
            color:#1e3a8a;
            font-weight:800;
            font-size:24px;
        ">
            {html.escape(initials)}
        </div>
        """
    st.markdown(
        f"""
        <a class="profile-link-card" href="#member_{index}" target="_self">
            <div class="member-card">
                {photo_html}
                <div class="member-name">{html.escape(member["name"])}</div>
                <div class="profile-mini-badge">{html.escape(member.get("focus", "Kelompok 7"))}</div>
                <div class="member-nim">{html.escape(member["nim"])}</div>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )
def show_landing_page():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none !important;
            }
            [data-testid="collapsedControl"] {
                display: none !important;
            }
            header[data-testid="stHeader"],
            div[data-testid="stToolbar"],
            footer {
                display: none !important;
                height: 0 !important;
            }
            html,
            body {
                overflow-x: hidden !important;
            }
            .block-container,
            div[data-testid="stMainBlockContainer"] {
                padding-top: 0.45rem !important;
                padding-bottom: 0 !important;
                max-height: 100vh !important;
                overflow: hidden !important;
            }
            div[data-testid="stVerticalBlock"] {
                gap: 0.35rem !important;
            }
            .landing-wrapper {
                margin-top: 0 !important;
                margin-bottom: 0.75rem !important;
            }
            .landing-card {
                margin-top: 0 !important;
            }
            .identity-box {
                margin-top: 1.15rem !important;
                margin-bottom: 0.35rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    inject_click_profile_css()
    render_all_profile_modals()
    logo_uri = get_file_data_uri(CAMPUS_LOGO_PATH)
    if logo_uri:
        logo_html = f'<img src="{logo_uri}" class="campus-logo" alt="ITSB Logo">'
    else:
        logo_html = '<div class="campus-logo" style="display:flex;align-items:center;justify-content:center;background:#e0ecff;color:#1e3a8a;font-weight:800;font-size:13px;border-radius:50%;">ITSB</div>'
    landing_header_html = "".join([
        '<div class="landing-wrapper">',
        '<div class="landing-card">',
        '<div class="top-campus-bar">',
        '<div class="campus-left">',
        logo_html,
        '<div class="campus-name-left">Institut Teknologi Sains Bandung</div>',
        '</div>',
        '<div class="campus-right"></div>',
        '</div>',
        '<div class="landing-title-center">',
        '<div class="project-title">📊 AUTO EDA ANALYTICS DASHBOARD</div>',
        '<div class="project-subtitle">Mini Project UAS Data Science Programming</div>',
        '<div class="group-badge">Kelompok 7</div>',
        '</div>',
        '</div>',
        '</div>'
    ])
    st.markdown(landing_header_html, unsafe_allow_html=True)
    member_cols = st.columns(4)
    

    for i, (col, member) in enumerate(zip(member_cols, TEAM_MEMBERS)):
        with col:
            render_member_card(member, i)
    identity_html = "".join([
        '<div class="landing-wrapper">',
        '<div class="identity-box">',
        '<div class="identity-grid">',
        '<a class="profile-link-card" href="#modal_matkul" target="_self">',
        '<div class="identity-item">',
        '<div class="identity-label">📚 Mata Kuliah</div>',
        '<div class="identity-value">Data Science Programming</div>',
        '</div>',
        '</a>',
        '<a class="profile-link-card" href="#modal_dosen" target="_self">',
        '<div class="identity-item">',
        '<div class="identity-label">👨‍🏫 Dosen Pengampu</div>',
        '<div class="identity-value">Bakti Siregar, M.Sc., CDS.</div>',
        '</div>',
        '</a>',
        '<a class="profile-link-card" href="#modal_prodi" target="_self">',
        '<div class="identity-item">',
        '<div class="identity-label">🎓 Program Studi</div>',
        '<div class="identity-value">Sains Data</div>',
        '</div>',
        '</a>',
        '</div>',
        '</div>',
        '</div>'
    ])
    st.markdown(identity_html, unsafe_allow_html=True)
    st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)
    if st.button("➡️ Lanjut Login", use_container_width=True):
        st.session_state.auth_page = "login"
        st.session_state.auth_mode = "login"
        st.rerun()
    st.stop()
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
def load_registered_users():
    os.makedirs(os.path.dirname(REGISTERED_USERS_PATH), exist_ok=True)
    if not os.path.exists(REGISTERED_USERS_PATH):
        return []
    try:
        with open(REGISTERED_USERS_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []
def save_registered_users(users):
    os.makedirs(os.path.dirname(REGISTERED_USERS_PATH), exist_ok=True)
    with open(REGISTERED_USERS_PATH, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)
def username_or_email_exists(username, email):
    username = username.strip().lower()
    email = email.strip().lower()
    for user in LOGIN_USERS:
        if username == user["username"].strip().lower() or email == user["email"].strip().lower():
            return True
    for user in load_registered_users():
        if username == user.get("username", "").strip().lower() or email == user.get("email", "").strip().lower():
            return True
    return False
def find_valid_user(username_input, password_input):
    username_input = username_input.strip().lower()
    password_input = password_input.strip()
    # Akun default anggota kelompok dan dosen tetap bisa dipakai.
    for member in LOGIN_USERS:
        valid_usernames = [
            member["username"].lower(),
            member["email"].lower()
        ]
        if username_input in valid_usernames and password_input == member["password"]:
            return member
    # Akun hasil registrasi.
    password_hash = hash_password(password_input)
    for user in load_registered_users():
        valid_usernames = [
            user.get("username", "").lower(),
            user.get("email", "").lower()
        ]
        if username_input in valid_usernames and password_hash == user.get("password_hash", ""):
            return {
                "name": user.get("name", user.get("username", "User")),
                "nim": "-",
                "username": user.get("username", ""),
                "email": user.get("email", ""),
                "password": "",
                "photo": ""
            }
    return None
def render_auth_mode_switcher():
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    col_login, col_register = st.columns(2)
    with col_login:
        if st.button("🔐 Login", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()
    with col_register:
        if st.button("📝 Registrasi Akun", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.rerun()
def render_login_form():
    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">🔐 Login Dashboard</div>
            <div class="login-subtitle">
                Masukkan username/email dan password. Jika belum punya akun, lakukan registrasi terlebih dahulu.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    username = st.text_input("Username / Email", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    col1, col2 = st.columns(2)
    with col1:
        login_clicked = st.button("🚀 Masuk Dashboard", use_container_width=True)
    with col2:
        back_clicked = st.button("⬅️ Kembali", use_container_width=True)
    if back_clicked:
        st.session_state.auth_page = "landing"
        st.rerun()
    if login_clicked:
        valid_user = find_valid_user(username, password)
        if valid_user is not None:
            st.session_state.is_logged_in = True
            st.session_state.logged_user = valid_user["name"]
            st.session_state.page = "Upload Data"
            st.success(f"Login berhasil. Selamat datang, {valid_user['name']}!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Username/email atau password salah, atau akun belum terdaftar.")
def render_register_form():
    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">📝 Registrasi Akun</div>
            <div class="login-subtitle">
                Buat akun terlebih dahulu, lalu gunakan username/email dan password tersebut untuk login.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    with st.form("registration_form", clear_on_submit=False):
        full_name = st.text_input("Nama Lengkap")
        username = st.text_input("Username Baru")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Konfirmasi Password", type="password")
        submitted = st.form_submit_button("✅ Daftar Akun", use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Sudah punya akun? Login", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()
    with col2:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.session_state.auth_page = "landing"
            st.rerun()
    if submitted:
        full_name_clean = full_name.strip()
        username_clean = username.strip()
        email_clean = email.strip().lower()
        password_clean = password.strip()
        confirm_clean = confirm_password.strip()
        if not full_name_clean or not username_clean or not email_clean or not password_clean:
            st.error("Semua field wajib diisi.")
            return
        if "@" not in email_clean or "." not in email_clean:
            st.error("Format email belum valid.")
            return
        if len(username_clean) < 4:
            st.error("Username minimal 4 karakter.")
            return
        if len(password_clean) < 6:
            st.error("Password minimal 6 karakter.")
            return
        if password_clean != confirm_clean:
            st.error("Konfirmasi password tidak sama.")
            return
        if username_or_email_exists(username_clean, email_clean):
            st.error("Username atau email sudah terdaftar. Gunakan yang lain.")
            return
        users = load_registered_users()
        users.append({
            "name": full_name_clean,
            "username": username_clean,
            "email": email_clean,
            "password_hash": hash_password(password_clean)
        })
        save_registered_users(users)
        st.success("Registrasi berhasil. Silakan login menggunakan username/email dan password yang baru dibuat.")
        st.session_state.auth_mode = "login"
        time.sleep(0.8)
        st.rerun()
def show_login_page():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="collapsedControl"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    render_auth_mode_switcher()
    if st.session_state.auth_mode == "register":
        render_register_form()
    else:
        render_login_form()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
