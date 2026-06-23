import re
import html
import streamlit as st


# =====================================================
# INSIGHT PAGE CSS — DARK PERMANENT
# =====================================================
def inject_insight_page_css():
    st.markdown(
        """
        <style>
            .insight-hero {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at 8% 0%, rgba(52, 217, 240, 0.16), transparent 34%),
                    radial-gradient(circle at 92% 8%, rgba(124, 110, 240, 0.17), transparent 36%),
                    linear-gradient(135deg, #020617 0%, #0f172a 52%, #111827 100%);
                border: 1px solid rgba(96, 165, 250, 0.28);
                border-radius: 24px;
                padding: 18px 22px;
                margin-bottom: 16px;
                box-shadow:
                    0 20px 52px rgba(0, 0, 0, 0.42),
                    0 0 36px rgba(59, 130, 246, 0.10);
            }

            .insight-hero-title {
                font-size: 24px;
                font-weight: 1000;
                color: #f8fafc !important;
                margin-bottom: 5px;
                line-height: 1.15;
            }

            .insight-hero-subtitle {
                font-size: 13px;
                color: #cbd5e1 !important;
                font-weight: 650;
                line-height: 1.55;
            }

            .insight-card {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at 0% 0%, rgba(52, 217, 240, 0.055), transparent 36%),
                    rgba(15, 23, 42, 0.92);
                border: 1px solid rgba(96, 165, 250, 0.26);
                border-left: 6px solid #38bdf8;
                border-radius: 22px;
                padding: 17px 19px;
                min-height: 158px;
                box-shadow:
                    0 16px 38px rgba(0, 0, 0, 0.34),
                    0 0 24px rgba(56, 189, 248, 0.06);
                color: #e2e8f0 !important;
                margin-bottom: 16px;
            }

            .insight-card::after {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(125,211,252,0.45), transparent);
            }

            .insight-card-title {
                margin: 0 0 12px 0;
                font-size: 16px;
                font-weight: 1000;
                color: #f8fafc !important;
                letter-spacing: 0.2px;
            }

            .insight-card-content {
                line-height: 1.75;
                font-size: 14.5px;
                color: #dbeafe !important;
                font-weight: 620;
            }

            .insight-card-content b,
            .insight-card-content strong {
                color: #ffffff !important;
                font-weight: 900;
            }

            .insight-empty-card {
                background: rgba(15, 23, 42, 0.92);
                border: 1px solid rgba(96, 165, 250, 0.28);
                border-left: 6px solid #f59e0b;
                border-radius: 22px;
                padding: 18px 20px;
                color: #e2e8f0 !important;
                box-shadow: 0 16px 38px rgba(0,0,0,0.34);
            }

            .insight-empty-title {
                font-size: 17px;
                font-weight: 1000;
                color: #f8fafc !important;
                margin-bottom: 8px;
            }

            .insight-empty-text {
                font-size: 14px;
                color: #cbd5e1 !important;
                line-height: 1.65;
                font-weight: 650;
            }

            .section-title,
            .section-title * {
                color: #ffffff !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def _strip_html_tags(text):
    """Bersihkan kalau insight lama masih berisi tag HTML mentah."""
    text = str(text)
    text = html.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</div\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</h[1-6]\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def _clean_insight_line(text):
    text = _strip_html_tags(text).strip()
    if not text:
        return ""

    if text.startswith(("•", "-", "*")):
        text = "• " + text.lstrip("•-* ").strip()

    return html.escape(text)


def _split_html_blob_if_needed(insights):
    """
    Kalau yang masuk ternyata satu blob HTML lama, ubah jadi list teks lagi.
    Ini mencegah HTML tampil sebagai kode mentah.
    """
    cleaned = []

    for item in insights:
        item_text = str(item).strip()
        if not item_text:
            cleaned.append("")
            continue

        if "<div" in item_text or "<h4" in item_text or "insight-card" in item_text:
            plain = _strip_html_tags(item_text)
            for line in plain.splitlines():
                line = line.strip()
                if line:
                    cleaned.append(line)
        else:
            cleaned.append(item_text)

    return cleaned


def show_insight_generator_page(
    df,
    file_name,
    file_ext,
    file_size,
    saved_file_path,
    numeric_cols,
    categorical_cols,
    date_cols,
    num_stats,
    cat_stats,
    insights,
    save_visualizations,
    render_summary_interpretation,
    calculate_health_score,
    get_health_label
):
    inject_insight_page_css()

    st.markdown(
        '<div class="section-title">🧠 Intelligent Insight Generator</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="insight-hero">
            <div class="insight-hero-title">🧠 Automated Data Insight</div>
            <div class="insight-hero-subtitle">
                Halaman ini menampilkan ringkasan insight otomatis berdasarkan struktur dataset,
                missing value, statistik numerik, kategori, korelasi, time series, dan insight akhir.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not insights:
        st.markdown(
            """
            <div class="insight-empty-card">
                <div class="insight-empty-title">⚠️ Insight belum tersedia</div>
                <div class="insight-empty-text">
                    Upload dataset terlebih dahulu atau pastikan proses analisis sudah berjalan agar insight otomatis dapat ditampilkan.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    section_titles = {
        "📊 DATASET OVERVIEW",
        "⚠ MISSING VALUE INSIGHT",
        "⚠️ MISSING VALUE INSIGHT",
        "🔢 NUMERICAL INSIGHT",
        "📋 CATEGORICAL INSIGHT",
        "🔗 CORRELATION INSIGHT",
        "📈 TIME SERIES INSIGHT",
        "💡 FINAL BUSINESS INSIGHT",
    }

    insights = _split_html_blob_if_needed(insights)

    cards = []
    current_title = None
    current_content = []

    def push_card():
        nonlocal current_title, current_content
        if current_title is None:
            return

        lines = [_clean_insight_line(x) for x in current_content if str(x).strip()]
        if not lines:
            lines = ["Belum ada detail insight tambahan pada bagian ini."]

        cards.append((current_title, lines))
        current_title = None
        current_content = []

    for item in insights:
        item_text = _strip_html_tags(str(item)).strip()

        if not item_text:
            continue

        if item_text in section_titles:
            push_card()
            current_title = item_text
            current_content = []
        else:
            current_content.append(item_text)

    push_card()

    if not cards:
        lines = [_clean_insight_line(x) for x in insights if str(x).strip()]
        cards = [("💡 Generated Insights", lines or ["Insight belum tersedia."])]

    # Render card satu per satu, bukan digabung jadi string besar.
    # Ini mencegah HTML tampil sebagai teks/kode mentah.
    for i in range(0, len(cards), 2):
        cols = st.columns(2, gap="medium")

        for col, card in zip(cols, cards[i:i + 2]):
            title, lines = card
            with col:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <h4 class="insight-card-title">{html.escape(str(title))}</h4>
                        <div class="insight-card-content">
                            {"<br>".join(lines)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
