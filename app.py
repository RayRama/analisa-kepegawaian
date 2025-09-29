import streamlit as st
import pandas as pd
import plotly.express as px
import re, os

st.set_page_config(page_title="Treemap Kepegawaian", layout="wide")

st.title("📊 Treemap Kepegawaian — OPD → Eselon → Jabatan → Golongan")

# ======================
# 1. Upload / Load Data
# ======================
uploaded_file = st.file_uploader("Upload file (CSV/Excel)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success(f"Loaded {uploaded_file.name} | Rows: {len(df)}")
else:
    st.warning("Silakan upload file CSV/Excel terlebih dahulu")
    st.stop()

# ======================
# 2. Konfigurasi kolom
# ======================
COL_OPD    = "satuan_kerja_nama"
COL_ESELON = "eselon"
COL_JAB    = "jabatan_nama"
COL_GOL    = "golongan"

UNIT_COLUMNS = []  # bisa ditambah kalau ada bidang/seksi

# ======================
# 3. Normalisasi teks
# ======================
def norm_space(x):
    if pd.isna(x): return None
    x = str(x).strip()
    x = re.sub(r"\s+", " ", x)
    return x if x else None

for c in [COL_OPD, COL_ESELON, COL_JAB, COL_GOL]:
    if c not in df.columns:
        st.error(f"Kolom '{c}' tidak ditemukan di data.")
        st.stop()
    df[c] = df[c].map(norm_space)

unit_cols_std = []
for i, col in enumerate(UNIT_COLUMNS):
    if col in df.columns:
        std_name = f"unit_l{i+1}"
        df[std_name] = df[col].map(norm_space).fillna(f"Unit L{i+1} Tidak Diketahui")
        unit_cols_std.append(std_name)

order_map = {"I":1,"II":2,"III":3,"III/IV":3.5,"IV":4,"NON-ESELON":9}
df["__eselon_ord__"] = df[COL_ESELON].str.upper().map(order_map).fillna(99)

# ======================
# 4. Audit data ringkas
# ======================
with st.expander("📋 Audit Data"):
    st.subheader("Distribusi Eselon (Global)")
    st.dataframe(df[COL_ESELON].value_counts().reset_index().rename(columns={"index":"Eselon","eselon":"Jumlah"}))

    st.subheader("Distribusi Golongan (Global)")
    st.dataframe(df[COL_GOL].value_counts().reset_index().rename(columns={"index":"Golongan","golongan":"Jumlah"}))

    st.subheader("Top 10 OPD (berdasarkan jumlah pegawai)")
    st.dataframe(df[COL_OPD].value_counts().head(10).reset_index().rename(columns={"index":"OPD","satuan_kerja_nama":"Jumlah"}))

    st.subheader("Contoh 10 Baris Data")
    st.dataframe(df[[COL_OPD, COL_ESELON, COL_GOL, COL_JAB]].head(10))

# ======================
# 5. Filter dropdown & multiselect
# ======================
eselon_options = ["[SEMUA]"] + sorted(df[COL_ESELON].dropna().unique().tolist())
eselon_filter = st.selectbox("Filter Eselon:", eselon_options)

opd_options = sorted(df[COL_OPD].dropna().unique().tolist())
opd_filter = st.multiselect("Filter OPD:", opd_options, default=opd_options)

golongan_options = sorted(df[COL_GOL].dropna().unique().tolist())
gol_filter = st.multiselect("Filter Golongan:", golongan_options, default=golongan_options)

# Apply filter
dff = df.copy()
if eselon_filter != "[SEMUA]":
    dff = dff[dff[COL_ESELON] == eselon_filter]
if opd_filter:
    dff = dff[dff[COL_OPD].isin(opd_filter)]
if gol_filter:
    dff = dff[dff[COL_GOL].isin(gol_filter)]

# Export tombol
st.download_button(
    label="💾 Download Data Filter (CSV)",
    data=dff.to_csv(index=False).encode("utf-8"),
    file_name=f"data_filter_{eselon_filter.replace('/','-')}.csv",
    mime="text/csv"
)

# ======================
# 6. Treemap Tingkat Tinggi: OPD → Eselon
# ======================
st.subheader("Treemap 1: OPD → Eselon")
agg1 = (dff.groupby([COL_OPD, COL_ESELON], dropna=False).size().reset_index(name="jumlah"))
agg1["__ord"] = agg1[COL_ESELON].str.upper().map(order_map).fillna(99)
agg1 = agg1.sort_values(["__ord", COL_OPD]).drop(columns=["__ord"])

fig1 = px.treemap(
    agg1,
    path=[COL_OPD, COL_ESELON],
    values="jumlah",
    hover_data={"jumlah": True},
    title="Treemap — OPD → Eselon"
)
fig1.update_layout(margin=dict(t=40,l=0,r=0,b=0))
fig1.update_traces(hovertemplate="<b>OPD:</b> %{parent}<br><b>Eselon:</b> %{label}<br><b>Jumlah:</b> %{value:,}<extra></extra>")
st.plotly_chart(fig1, use_container_width=True)

# ======================
# 7. Treemap Detail: OPD → Eselon → (Unit …) → Jabatan
# ======================
st.subheader("Treemap 2: OPD → Eselon → Jabatan")
path_hierarchy = [COL_OPD, COL_ESELON] + unit_cols_std + [COL_JAB]

agg2 = (dff.groupby(path_hierarchy, dropna=False).size().reset_index(name="jumlah"))

for col in path_hierarchy:
    agg2[col] = agg2[col].fillna("Tidak Diketahui")
    agg2[col] = agg2[col].replace("", "Tidak Diketahui")

if COL_ESELON in path_hierarchy:
    ord_map_df = df[[COL_ESELON, "__eselon_ord__"]].drop_duplicates().rename(columns={"__eselon_ord__":"__ord"})
    agg2 = agg2.merge(ord_map_df, on=COL_ESELON, how="left").sort_values(["__ord"]).drop(columns=["__ord"])

fig2 = px.treemap(
    agg2,
    path=path_hierarchy,
    values="jumlah",
    hover_data={"jumlah": True},
    title="Treemap — OPD → Eselon → Jabatan"
)
fig2.update_layout(margin=dict(t=40,l=0,r=0,b=0))
fig2.update_traces(hovertemplate="<b>Jabatan:</b> %{label}<br><b>Jumlah:</b> %{value:,}<extra></extra>")
st.plotly_chart(fig2, use_container_width=True)

# ======================
# 8. Treemap Tambahan: OPD → Golongan
# ======================
st.subheader("Treemap 3: OPD → Golongan")
agg3 = (dff.groupby([COL_OPD, COL_GOL], dropna=False).size().reset_index(name="jumlah"))

for col in [COL_OPD, COL_GOL]:
    agg3[col] = agg3[col].fillna("Tidak Diketahui")
    agg3[col] = agg3[col].replace("", "Tidak Diketahui")

fig3 = px.treemap(
    agg3,
    path=[COL_OPD, COL_GOL],
    values="jumlah",
    hover_data={"jumlah": True},
    title="Treemap — OPD → Golongan"
)
fig3.update_layout(margin=dict(t=40,l=0,r=0,b=0))
fig3.update_traces(hovertemplate="<b>OPD:</b> %{parent}<br><b>Golongan:</b> %{label}<br><b>Jumlah:</b> %{value:,}<extra></extra>")
st.plotly_chart(fig3, use_container_width=True)

# ======================
# 9. Pivot Table: OPD × Golongan
# ======================
st.subheader("📑 Ringkasan Tabel Pivot — OPD × Golongan")
pivot = pd.pivot_table(dff, 
                       index=COL_OPD, 
                       columns=COL_GOL, 
                       values=COL_JAB, 
                       aggfunc="count", 
                       fill_value=0,
                       margins=True, 
                       margins_name="Total")
st.dataframe(pivot)

# Export pivot
st.download_button(
    label="💾 Download Pivot OPD × Golongan (CSV)",
    data=pivot.to_csv().encode("utf-8"),
    file_name="pivot_opd_golongan.csv",
    mime="text/csv"
)
