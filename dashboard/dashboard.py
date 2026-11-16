import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Dashboard E-Commerce Olist", page_icon="🛒", layout="wide")

BLUE, ORANGE, GREY, INK2 = "#2a78d6", "#eb6834", "#b9b8b2", "#52514e"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GREY,
                     "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left"})


@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "main_data.csv")
    df = pd.read_csv(path, parse_dates=["order_purchase_timestamp", "purchase_month"])
    return df


df = load_data()

# Sidebar filter
st.sidebar.header("Filter")
min_d, max_d = df["order_purchase_timestamp"].dt.date.min(), df["order_purchase_timestamp"].dt.date.max()
date_range = st.sidebar.date_input("Rentang tanggal pembelian", (min_d, max_d), min_value=min_d, max_value=max_d)
if len(date_range) != 2:
    st.info("Pilih tanggal awal dan akhir pada filter di sidebar.")
    st.stop()
states = sorted(df["customer_state"].unique())
sel_states = st.sidebar.multiselect("State pelanggan", states, default=states)

mask = (df["order_purchase_timestamp"].dt.date >= date_range[0]) & (df["order_purchase_timestamp"].dt.date <= date_range[1]) \
       & df["customer_state"].isin(sel_states)
data = df[mask]
if data.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()
orders = data.drop_duplicates("order_id")

# Header
st.title("Dashboard Analisis E-Commerce Olist")
st.caption("Pesanan berstatus delivered, Januari 2017 sampai Agustus 2018. Nilai dalam Real Brasil (R$).")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jumlah pesanan", f"{orders['order_id'].nunique():,}")
c2.metric("Total pendapatan", f"R$ {data['price'].sum():,.0f}")
c3.metric("Rata-rata review", f"{orders['review_score'].mean():.2f}")
c4.metric("Pesanan terlambat", f"{orders['is_late'].mean() * 100:.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(["Kategori produk", "Pengiriman", "Segmentasi RFM", "Sebaran geografis"])

# Tab 1: kategori
with tab1:
    st.subheader("Kategori dengan pendapatan terbesar dan rata-rata review")
    n_top = st.slider("Jumlah kategori ditampilkan", 5, 15, 10)
    cat = (data.groupby("category").agg(revenue=("price", "sum"), items=("order_id", "count"),
                                        avg_review=("review_score", "mean")).sort_values("revenue", ascending=False))
    t = cat.head(n_top).sort_values("revenue")
    avg_all = orders["review_score"].mean()
    fig, ax = plt.subplots(1, 2, figsize=(12, 0.45 * n_top + 2), sharey=True, gridspec_kw={"width_ratios": [1.5, 1]})
    ax[0].barh(t.index, t["revenue"] / 1e6, color=BLUE, height=0.65)
    for y, v in enumerate(t["revenue"] / 1e6):
        ax[0].text(v + 0.02, y, f"{v:.2f} jt", va="center", fontsize=8, color=INK2)
    ax[0].set_title("Total pendapatan (R$ juta)")
    ax[0].set_xlim(0, t["revenue"].max() / 1e6 * 1.2)
    ax[1].barh(t.index, t["avg_review"], color=[ORANGE if v < avg_all else BLUE for v in t["avg_review"]], height=0.65)
    ax[1].axvline(avg_all, color=INK2, ls="--", lw=1)
    for y, v in enumerate(t["avg_review"]):
        ax[1].text(max(v, avg_all) + 0.08, y, f"{v:.2f}", va="center", fontsize=8, color=INK2)
    ax[1].set_xlim(0, 5)
    ax[1].set_title(f"Rata-rata review (garis putus = rata-rata {avg_all:.2f})")
    plt.tight_layout()
    st.pyplot(fig)
    st.caption("Batang review oranye berarti di bawah rata-rata keseluruhan pada filter yang dipilih.")
    with st.expander("Lihat tabel"):
        st.dataframe(t.sort_values("revenue", ascending=False).round(2))

# Tab 2: pengiriman
with tab2:
    st.subheader("Keterlambatan pengiriman dan dampaknya pada review")
    min_orders = st.slider("Minimal pesanan per state", 1, 1000, 300, step=50)
    s = (orders.groupby("customer_state").agg(orders=("order_id", "count"), late_pct=("is_late", lambda x: x.mean() * 100),
                                              avg_review=("review_score", "mean")))
    s = s[s["orders"] >= min_orders].sort_values("late_pct", ascending=False).head(10).sort_values("late_pct")
    overall = orders["is_late"].mean() * 100
    col_a, col_b = st.columns(2)
    with col_a:
        if s.empty:
            st.info("Tidak ada state yang memenuhi minimal pesanan.")
        else:
            fig, ax = plt.subplots(figsize=(6, 4.5))
            ax.barh(s.index, s["late_pct"], color=[ORANGE if v > overall else BLUE for v in s["late_pct"]], height=0.65)
            ax.axvline(overall, color=INK2, ls="--", lw=1)
            for y, (v, n) in enumerate(zip(s["late_pct"], s["orders"])):
                ax.text(v + 0.2, y, f"{v:.1f}% (n={n:,})", va="center", fontsize=8, color=INK2)
            ax.set_xlim(0, s["late_pct"].max() * 1.35)
            ax.set_title(f"State dengan keterlambatan tertinggi (rata-rata {overall:.1f}%)")
            ax.set_xlabel("Pesanan terlambat (%)")
            plt.tight_layout()
            st.pyplot(fig)
    with col_b:
        o = orders.copy()
        labels = ["Awal > 14 hr", "Awal 7-14 hr", "Awal 0-7 hr", "Telat 1-3 hr", "Telat 4-7 hr", "Telat > 7 hr"]
        o["bin"] = pd.cut(o["delay_days"], [-np.inf, -14, -7, 0, 3, 7, np.inf], labels=labels)
        b = o.groupby("bin", observed=False).agg(orders=("order_id", "count"), avg_review=("review_score", "mean"))
        fig, ax = plt.subplots(figsize=(6, 4.5))
        ax.bar(b.index.astype(str), b["avg_review"].fillna(0), color=[BLUE if "Awal" in l else ORANGE for l in b.index], width=0.65)
        for x, v in enumerate(b["avg_review"].fillna(0)):
            ax.text(x, v + 0.06, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
        ax.set_ylim(0, 5)
        ax.set_title("Review turun saat pesanan melewati estimasi")
        ax.set_ylabel("Rata-rata review")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
    on, late = orders[~orders["is_late"]]["review_score"].mean(), orders[orders["is_late"]]["review_score"].mean()
    st.caption(f"Rata-rata review tepat waktu {on:.2f} vs terlambat {late:.2f}.")

# Tab 3: RFM 
with tab3:
    st.subheader("Segmentasi pelanggan (RFM, tanggal acuan 1 September 2018)")
    st.markdown("**Recency** = hari sejak pembelian terakhir, **Frequency** = jumlah pesanan, **Monetary** = total harga + ongkir. "
                "Segmen dibuat dengan aturan manual (tanpa machine learning).")
    ref = pd.Timestamp("2018-09-01")
    rfm = (data.groupby("customer_unique_id").agg(last_order=("order_purchase_timestamp", "max"),
                                                  frequency=("order_id", "nunique"), monetary=("total_value", "sum")).reset_index())
    rfm["recency"] = (ref - rfm["last_order"]).dt.days
    high = rfm["monetary"].quantile(0.75)

    def segment(r):
        if r.frequency >= 2:
            return "Loyal (repeat, aktif)" if r.recency <= 180 else "Repeat (perlu diaktifkan)"
        if r.recency <= 90:
            return "Baru bernilai tinggi" if r.monetary >= high else "Baru"
        if r.recency <= 270:
            return "Win-back bernilai tinggi" if r.monetary >= high else "Mulai pasif"
        return "Hilang (> 270 hari)"

    rfm["segment"] = rfm.apply(segment, axis=1)
    order = ["Loyal (repeat, aktif)", "Repeat (perlu diaktifkan)", "Baru bernilai tinggi", "Baru",
             "Win-back bernilai tinggi", "Mulai pasif", "Hilang (> 270 hari)"]
    seg = rfm.groupby("segment").agg(pelanggan=("customer_unique_id", "count"), revenue=("monetary", "sum")).reindex(order).fillna(0)
    seg["pelanggan_%"] = seg["pelanggan"] / seg["pelanggan"].sum() * 100
    seg["revenue_%"] = seg["revenue"] / seg["revenue"].sum() * 100
    y, h = np.arange(len(seg))[::-1], 0.36
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.barh(y + h / 2, seg["pelanggan_%"], height=h, color=GREY, label="% pelanggan")
    ax.barh(y - h / 2, seg["revenue_%"], height=h, color=BLUE, label="% pendapatan")
    for yy, a, b in zip(y, seg["pelanggan_%"], seg["revenue_%"]):
        ax.text(a + 0.4, yy + h / 2, f"{a:.1f}%", va="center", fontsize=8, color=INK2)
        ax.text(b + 0.4, yy - h / 2, f"{b:.1f}%", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(seg.index)
    ax.set_xlim(0, max(seg["pelanggan_%"].max(), seg["revenue_%"].max()) * 1.25)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Porsi pelanggan vs porsi pendapatan per segmen")
    plt.tight_layout()
    st.pyplot(fig)
    st.caption(f"Pelanggan bernilai tinggi = total belanja di kuartil teratas (>= R$ {high:,.0f}).")
    with st.expander("Lihat tabel"):
        st.dataframe(seg.round(1))

# Tab 4: geospatial
with tab4:
    st.subheader("Sebaran pesanan dan keterlambatan per state")
    g = (orders.dropna(subset=["lat", "lng"]).groupby("customer_state")
         .agg(lat=("lat", "mean"), lng=("lng", "mean"), orders=("order_id", "count"),
              late_pct=("is_late", lambda x: x.mean() * 100)).reset_index())
    fig, ax = plt.subplots(figsize=(7.5, 7))
    sc = ax.scatter(g["lng"], g["lat"], s=60 + g["orders"] / 12, c=g["late_pct"], cmap="Oranges", vmin=0,
                    edgecolor="white", linewidth=1.2, alpha=0.95)
    for _, r in g.iterrows():
        ax.annotate(r["customer_state"], (r["lng"], r["lat"]), ha="center", va="center", fontsize=8)
    plt.colorbar(sc, ax=ax, shrink=0.6, label="Pesanan terlambat (%)")
    ax.set_xlabel("Bujur")
    ax.set_ylabel("Lintang")
    ax.set_title("Ukuran titik = jumlah pesanan, warna = % terlambat")
    plt.tight_layout()
    st.pyplot(fig)
