import streamlit as st


def show_empty_dashboard_page():
    # =====================================================
    # EMPTY DASHBOARD STATE
    # Tampilan awal ketika dataset belum diupload.
    # Dibuat lebih rapi, modern, dan tetap ringan.
    # =====================================================

    st.markdown(
        """
        <style>
            .empty-dashboard-wrap {
                max-width: 1150px;
                margin: 0 auto;
                padding-top: 2px;
            }

            .empty-hero {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at 8% 10%, rgba(36, 209, 239, 0.30), transparent 35%),
                    radial-gradient(circle at 92% 0%, rgba(109, 40, 217, 0.28), transparent 35%),
                    linear-gradient(135deg, #0f172a 0%, #1d4ed8 48%, #6d28d9 100%);
                color: white;
                padding: 26px 28px;
                border-radius: 28px;
                box-shadow:
                    0 24px 58px rgba(37, 99, 235, 0.28),
                    0 10px 24px rgba(15, 23, 42, 0.14);
                margin-bottom: 16px;
                border: 1px solid rgba(255,255,255,0.18);
            }

            .empty-hero::before {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(255,255,255,0.18),
                    transparent
                );
                transform: translateX(-100%);
                animation: emptyShimmer 5s ease-in-out infinite;
                pointer-events: none;
            }

            @keyframes emptyShimmer {
                0% { transform: translateX(-110%); }
                45% { transform: translateX(120%); }
                100% { transform: translateX(120%); }
            }

            .empty-hero-content {
                position: relative;
                z-index: 1;
                display: flex;
                justify-content: space-between;
                gap: 18px;
                align-items: center;
            }

            .empty-title {
                font-size: 30px;
                font-weight: 950;
                line-height: 1.1;
                margin-bottom: 8px;
                letter-spacing: -0.4px;
            }

            .empty-subtitle {
                font-size: 14px;
                color: #dbeafe;
                line-height: 1.6;
                font-weight: 600;
                max-width: 680px;
            }

            .empty-status-pill {
                min-width: 210px;
                background: rgba(255,255,255,0.14);
                border: 1px solid rgba(255,255,255,0.24);
                border-radius: 20px;
                padding: 16px 18px;
                text-align: center;
                box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
                backdrop-filter: blur(14px);
            }

            .empty-pill-label {
                font-size: 11px;
                font-weight: 800;
                color: #bfdbfe;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                margin-bottom: 4px;
            }

            .empty-pill-value {
                font-size: 22px;
                font-weight: 950;
                color: #ffffff;
            }

            .empty-alert {
                background: linear-gradient(135deg, #eff6ff, #eef2ff);
                color: #1e3a8a;
                border: 1px solid rgba(37, 99, 235, 0.16);
                border-left: 6px solid #2563eb;
                padding: 14px 16px;
                border-radius: 18px;
                font-size: 14px;
                font-weight: 800;
                margin-bottom: 14px;
                box-shadow: 0 8px 20px rgba(37,99,235,0.08);
            }

            .empty-kpi {
                background: rgba(255,255,255,0.94);
                border: 1px solid rgba(37, 99, 235, 0.13);
                border-radius: 22px;
                padding: 18px 18px;
                min-height: 135px;
                box-shadow: 0 10px 26px rgba(15,23,42,0.08);
                transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            }

            .empty-kpi:hover {
                transform: translateY(-5px);
                border-color: rgba(37, 99, 235, 0.30);
                box-shadow: 0 16px 36px rgba(37,99,235,0.16);
            }

            .empty-kpi-icon {
                font-size: 28px;
                margin-bottom: 7px;
            }

            .empty-kpi-label {
                font-size: 12px;
                color: #64748b;
                font-weight: 850;
                text-transform: uppercase;
                letter-spacing: 0.7px;
            }

            .empty-kpi-value {
                font-size: 24px;
                color: #0f172a;
                font-weight: 950;
                margin-top: 4px;
                line-height: 1.15;
            }

            .empty-section-title {
                font-size: 15px;
                font-weight: 950;
                color: #0f172a;
                margin: 16px 0 10px 0;
            }

            .empty-feature-card {
                background: rgba(255,255,255,0.94);
                border: 1px solid rgba(37,99,235,0.12);
                border-radius: 20px;
                padding: 16px 17px;
                min-height: 165px;
                box-shadow: 0 10px 26px rgba(15,23,42,0.08);
            }

            .empty-feature-title {
                font-size: 14px;
                font-weight: 950;
                color: #1e3a8a;
                margin-bottom: 8px;
            }

            .empty-feature-text {
                font-size: 13px;
                color: #334155;
                line-height: 1.65;
                font-weight: 600;
            }

            .empty-step {
                display: flex;
                align-items: flex-start;
                gap: 10px;
                margin-bottom: 9px;
            }

            .empty-step-num {
                flex: 0 0 26px;
                height: 26px;
                width: 26px;
                border-radius: 999px;
                background: linear-gradient(135deg, #1d4ed8, #6d28d9);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 950;
                box-shadow: 0 6px 14px rgba(37,99,235,0.20);
            }

            .empty-step-text {
                font-size: 13px;
                color: #334155;
                font-weight: 650;
                line-height: 1.45;
            }

            .empty-footer-note {
                margin-top: 12px;
                background: linear-gradient(135deg, #ecfeff, #eff6ff);
                border: 1px solid rgba(14, 165, 233, 0.20);
                color: #0f3a68;
                border-radius: 18px;
                padding: 12px 14px;
                font-size: 13px;
                font-weight: 750;
            }

            @media (prefers-color-scheme: dark) {
                .empty-alert,
                .empty-kpi,
                .empty-feature-card,
                .empty-footer-note {
                    background: rgba(15,23,42,0.92);
                    border-color: rgba(96,165,250,0.25);
                    color: #cbd5e1;
                }

                .empty-section-title,
                .empty-kpi-value,
                .empty-feature-title {
                    color: #93c5fd;
                }

                .empty-feature-text,
                .empty-step-text,
                .empty-kpi-label {
                    color: #cbd5e1;
                }
            }

            @media (max-width: 900px) {
                .empty-hero-content {
                    flex-direction: column;
                    align-items: stretch;
                }

                .empty-status-pill {
                    min-width: unset;
                }

                .empty-title {
                    font-size: 24px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="empty-dashboard-wrap">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="empty-hero">
            <div class="empty-hero-content">
                <div>
                    <div class="empty-title">📊 Auto EDA Analytics Dashboard</div>
                    <div class="empty-subtitle">
                        Dashboard siap membantu membaca dataset, mengecek kualitas data,
                        membuat statistik deskriptif, visualisasi otomatis, insight, time series,
                        hingga export report.
                    </div>
                </div>
                <div class="empty-status-pill">
                    <div class="empty-pill-label">Current Status</div>
                    <div class="empty-pill-value">Dataset Needed</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="empty-alert">
            📁 Silakan upload dataset terlebih dahulu melalui menu <b>Data Management → Upload Data</b>
            agar seluruh fitur dashboard aktif.
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="empty-kpi">
                <div class="empty-kpi-icon">📦</div>
                <div class="empty-kpi-label">Supported Format</div>
                <div class="empty-kpi-value">CSV / XLSX / TXT</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="empty-kpi">
                <div class="empty-kpi-icon">⚙️</div>
                <div class="empty-kpi-label">Dashboard Type</div>
                <div class="empty-kpi-value">Auto EDA</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
            <div class="empty-kpi">
                <div class="empty-kpi-icon">🚀</div>
                <div class="empty-kpi-label">Analytics Mode</div>
                <div class="empty-kpi-value">BI Style</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="empty-section-title">✨ Fitur yang akan aktif setelah dataset diupload</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown(
            """
            <div class="empty-feature-card">
                <div class="empty-feature-title">📌 Data Management</div>
                <div class="empty-feature-text">
                    Menampilkan file information, data preview, dataset information,
                    dan ringkasan struktur data secara otomatis.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with f2:
        st.markdown(
            """
            <div class="empty-feature-card">
                <div class="empty-feature-title">📈 Visualization Analytics</div>
                <div class="empty-feature-text">
                    Membuat grafik numerical, categorical, bivariate,
                    categorical vs numerical, dan time series analytics.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with f3:
        st.markdown(
            """
            <div class="empty-feature-card">
                <div class="empty-feature-title">🧠 Insight & Report</div>
                <div class="empty-feature-text">
                    Menghasilkan insight otomatis, interpretasi grafik,
                    dan export hasil analisis ke PDF, HTML, Excel, atau CSV.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="empty-section-title">🧭 Cara mulai menggunakan dashboard</div>', unsafe_allow_html=True)

    step_col, action_col = st.columns([1.35, 1])

    with step_col:
        st.markdown(
            """
            <div class="empty-feature-card">
                <div class="empty-step">
                    <div class="empty-step-num">1</div>
                    <div class="empty-step-text">Klik tombol <b>Upload Dataset Sekarang</b> atau buka menu Data Management.</div>
                </div>
                <div class="empty-step">
                    <div class="empty-step-num">2</div>
                    <div class="empty-step-text">Pilih file CSV, XLSX, atau TXT yang ingin dianalisis.</div>
                </div>
                <div class="empty-step">
                    <div class="empty-step-num">3</div>
                    <div class="empty-step-text">Dashboard akan otomatis membaca data dan mengaktifkan semua fitur analisis.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with action_col:
        st.markdown(
            """
            <div class="empty-feature-card">
                <div class="empty-feature-title">☁️ Ready to Analyze?</div>
                <div class="empty-feature-text">
                    Upload dataset agar dashboard dapat menampilkan KPI, statistik,
                    grafik, interpretasi, dan report otomatis.
                </div>
                <div class="empty-footer-note">
                    Tips: gunakan dataset yang memiliki minimal satu kolom numerik agar visualisasi lebih lengkap.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("📁 Upload Dataset Sekarang", use_container_width=True):
            st.session_state.page = "Upload Data"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

