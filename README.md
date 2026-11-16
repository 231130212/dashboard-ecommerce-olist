# Proyek Analisis Data: E-Commerce Public Dataset (Olist)

Proyek akhir kelas Belajar Analisis Data dengan Python. Analisis mencakup pertanyaan bisnis SMART, data wrangling, EDA, visualisasi, analisis lanjutan (RFM, geospatial, binning), serta dashboard interaktif dengan Streamlit.

## Pertanyaan Bisnis
1. 10 kategori produk apa yang menghasilkan pendapatan terbesar pada Januari 2017 sampai Agustus 2018, dan berapa rata-rata review-nya?
2. Berapa persentase pesanan terlambat per state pada periode yang sama, dan berapa selisih review antara pesanan terlambat dan tepat waktu?
3. Bagaimana segmentasi pelanggan berdasarkan RFM (acuan 1 September 2018) dan segmen mana yang menyumbang pendapatan terbesar?

## Struktur Direktori
```
submission
├── dashboard
│   ├── main_data.csv
│   └── dashboard.py
├── data
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── products_dataset.csv
│   └── product_category_name_translation.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```
`dashboard/main_data.csv` dihasilkan oleh `notebook.ipynb` (bagian Cleaning Data) dan menjadi satu-satunya sumber data dashboard.

## Setup Environment
Disarankan Python 3.10 atau lebih baru.

```
python -m venv venv
# Windows:  venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Dashboard
Dari folder `submission`:

```
cd dashboard
streamlit run dashboard.py
```

Dashboard terbuka di `http://localhost:8501`. Fitur: filter rentang tanggal dan state, empat tab (kategori produk, pengiriman, segmentasi RFM, sebaran geografis).

## Menjalankan Notebook
Buka `notebook.ipynb` dari folder `submission` (agar path `data/` dan `dashboard/` terbaca), lalu jalankan semua sel. Untuk Jupyter perlu tambahan `pip install jupyter`.

## Deploy ke Streamlit Community Cloud
1. Unggah folder proyek ke repositori GitHub (`requirements.txt` berada di root repositori).
2. Masuk ke https://share.streamlit.io, pilih **New app**, pilih repositori dan branch.
3. Isi **Main file path** dengan `dashboard/dashboard.py`, lalu **Deploy**.
4. Salin tautan aplikasi ke `url.txt`.
