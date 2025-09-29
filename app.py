import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re, os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Treemap Kepegawaian", layout="wide")

st.title("📊 Treemap Kepegawaian — OPD → Eselon → Jabatan → Golongan")

# Add info about debugging
with st.expander("ℹ️ Cara Debugging"):
    st.write("""
    **Jika ada error di console browser:**
    1. Buka Developer Tools (F12)
    2. Lihat tab Console untuk error details
    3. Cek tab Debug Information di bawah untuk data info
    4. Pastikan semua kolom yang diperlukan ada di data
    
    **Error yang sering muncul:**
    - `customdata[0]` not found: Masalah hovertemplate
    - `label` not found: Masalah dengan data aggregation
    - Column not found: Periksa nama kolom di data
    """)

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
    logger.info(f"Data loaded: {len(df)} rows, columns: {list(df.columns)}")
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
# 4.5. Debug Information
# ======================
with st.expander("🔍 Debug Information"):
    st.subheader("Data Info")
    st.write(f"**Total Rows:** {len(df)}")
    st.write(f"**Columns:** {list(df.columns)}")
    st.write(f"**Data Types:**")
    st.write(df.dtypes)
    
    st.subheader("Sample Data for Treemap")
    st.write("**First 5 rows of aggregated data:**")
    if 'agg1' in locals():
        st.write("Treemap 1 (OPD → Eselon):")
        st.dataframe(agg1.head())
        st.write(f"**Jumlah values sample:** {agg1['jumlah'].tolist()[:10]}")
        st.write(f"**Jumlah min/max:** {agg1['jumlah'].min()}/{agg1['jumlah'].max()}")
    if 'agg2' in locals():
        st.write("Treemap 2 (OPD → Eselon → Jabatan):")
        st.dataframe(agg2.head())
        st.write(f"**Jumlah values sample:** {agg2['jumlah'].tolist()[:10]}")
    if 'agg3' in locals():
        st.write("Treemap 3 (OPD → Golongan):")
        st.dataframe(agg3.head())
        st.write(f"**Jumlah values sample:** {agg3['jumlah'].tolist()[:10]}")
    
    st.subheader("Console Logs")
    st.write("**Check browser console (F12) for detailed logs**")
    st.write("**Common issues:**")
    st.write("- Hovertemplate variables not found: %{parent}, %{label}, %{value}")
    st.write("- Data aggregation issues: Check if columns exist")
    st.write("- Plotly version compatibility: Try updating plotly")

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

logger.info(f"Treemap 1 data shape: {agg1.shape}")
logger.info(f"Treemap 1 columns: {list(agg1.columns)}")
logger.info(f"Sample data:\n{agg1.head()}")
logger.info(f"Jumlah values: {agg1['jumlah'].tolist()[:10]}")
logger.info(f"Jumlah min/max: {agg1['jumlah'].min()}/{agg1['jumlah'].max()}")

# Create treemap with simple approach first
fig1 = px.treemap(
    agg1,
    path=[COL_OPD, COL_ESELON],
    values="jumlah",
    title="Treemap — OPD → Eselon"
)
fig1.update_layout(margin=dict(t=40,l=0,r=0,b=0))

# Alternative 1: Show values directly on the treemap
fig1.update_traces(
    textinfo="label+value",
    texttemplate="%{label}<br>%{value}",
    textfont_size=12,
    textposition="middle center"
)

# Try different hovertemplate approaches
try:
    # Method 1: Try with customdata (current working approach)
    fig1.data[0].customdata = agg1[['jumlah']].values
    fig1.update_traces(
        textinfo="label+value",
        hovertemplate="<b>%{label}</b><br>Jumlah: %{customdata[0]:,}<extra></extra>"
    )
    logger.info("Treemap 1 hovertemplate with customdata added successfully")
    
    # Test if hovertemplate is working by checking the actual values
    logger.info(f"Sample customdata values: {fig1.data[0].customdata[:5].flatten()}")
    logger.info(f"Sample labels: {fig1.data[0].labels[:5]}")
    
    # Try alternative hovertemplate formats
    try:
        # Alternative 1: Without formatting
        fig1.data[0].hovertemplate = "<b>%{label}</b><br>Jumlah: %{customdata[0]}<extra></extra>"
        logger.info("Alternative hovertemplate 1 applied")
    except Exception as e:
        logger.error(f"Error with alternative 1: {e}")
        
    try:
        # Alternative 2: With different customdata access
        fig1.data[0].hovertemplate = "<b>%{label}</b><br>Jumlah: %{customdata}<extra></extra>"
        logger.info("Alternative hovertemplate 2 applied")
    except Exception as e:
        logger.error(f"Error with alternative 2: {e}")
    
except Exception as e:
    logger.error(f"Error with customdata hovertemplate: {e}")
    try:
        # Method 2: Try with direct value
        fig1.update_traces(
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<extra></extra>"
        )
        logger.info("Treemap 1 hovertemplate with direct value added successfully")
    except Exception as e2:
        logger.error(f"Error with direct value hovertemplate: {e2}")
        try:
            # Method 3: Try with hover_data
            fig1 = px.treemap(
                agg1,
                path=[COL_OPD, COL_ESELON],
                values="jumlah",
                hover_data={"jumlah": True},
                title="Treemap — OPD → Eselon"
            )
            fig1.update_layout(margin=dict(t=40,l=0,r=0,b=0))
            fig1.update_traces(
                textinfo="label+value",
                hovertemplate="<b>%{label}</b><br>Jumlah: %{customdata[0]:,}<extra></extra>"
            )
            logger.info("Treemap 1 recreated with hover_data approach")
        except Exception as e3:
            logger.error(f"Error with hover_data approach: {e3}")
            # Final fallback: just textinfo
            fig1.update_traces(textinfo="label+value")
            logger.info("Treemap 1 created with textinfo only")

logger.info(f"Treemap 1 data count: {len(fig1.data)}")
if len(fig1.data) > 0:
    logger.info(f"Treemap 1 trace type: {type(fig1.data[0])}")
    logger.info(f"Treemap 1 trace name: {fig1.data[0].name}")
    logger.info(f"Treemap 1 values count: {len(fig1.data[0].values) if hasattr(fig1.data[0], 'values') else 'N/A'}")
    logger.info(f"Treemap 1 hovertemplate: {fig1.data[0].hovertemplate}")
    logger.info(f"Treemap 1 textinfo: {fig1.data[0].textinfo}")
    if hasattr(fig1.data[0], 'customdata') and fig1.data[0].customdata is not None:
        logger.info(f"Treemap 1 customdata shape: {fig1.data[0].customdata.shape if hasattr(fig1.data[0].customdata, 'shape') else 'N/A'}")
        logger.info(f"Treemap 1 customdata sample: {fig1.data[0].customdata[:5] if hasattr(fig1.data[0].customdata, '__getitem__') else 'N/A'}")
    else:
        logger.info("Treemap 1 has no customdata")

# Debug: Show data before plotting
with st.expander("🔍 Debug Treemap 1 Data"):
    st.write("**Aggregated Data:**")
    st.dataframe(agg1.head(10))
    st.write(f"**Total rows:** {len(agg1)}")
    st.write(f"**Sample values:** {agg1['jumlah'].tolist()[:10]}")
    st.write(f"**OPD unique count:** {agg1[COL_OPD].nunique()}")
    st.write(f"**Eselon unique count:** {agg1[COL_ESELON].nunique()}")
    st.write("**Sample OPD names:**")
    st.write(agg1[COL_OPD].unique()[:5].tolist())
    st.write("**Sample Eselon values:**")
    st.write(agg1[COL_ESELON].unique()[:5].tolist())
    
    # Test with simple data
    st.write("**Test with simple data:**")
    test_data = agg1.head(5).copy()
    st.dataframe(test_data)
    
    # Create test treemap with different hovertemplate approaches
    st.write("**Test 1: Basic treemap**")
    try:
        test_fig1 = px.treemap(
            test_data,
            path=[COL_OPD, COL_ESELON],
            values="jumlah",
            title="Test 1: Basic"
        )
        st.plotly_chart(test_fig1, use_container_width=True)
        st.success("Test 1: Basic treemap created successfully!")
    except Exception as e:
        st.error(f"Error creating test 1: {e}")
    
    st.write("**Test 2: With hover_data**")
    try:
        test_fig2 = px.treemap(
            test_data,
            path=[COL_OPD, COL_ESELON],
            values="jumlah",
            hover_data={"jumlah": True},
            title="Test 2: With hover_data"
        )
        test_fig2.update_traces(
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>Jumlah: %{customdata[0]:,}<extra></extra>"
        )
        st.plotly_chart(test_fig2, use_container_width=True)
        st.success("Test 2: With hover_data created successfully!")
    except Exception as e:
        st.error(f"Error creating test 2: {e}")
    
    st.write("**Test 3: With direct value**")
    try:
        test_fig3 = px.treemap(
            test_data,
            path=[COL_OPD, COL_ESELON],
            values="jumlah",
            title="Test 3: Direct value"
        )
        test_fig3.update_traces(
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<extra></extra>"
        )
        st.plotly_chart(test_fig3, use_container_width=True)
        st.success("Test 3: Direct value created successfully!")
    except Exception as e:
        st.error(f"Error creating test 3: {e}")
    
    st.write("**Test 4: With customdata (same as main)**")
    try:
        test_fig4 = px.treemap(
            test_data,
            path=[COL_OPD, COL_ESELON],
            values="jumlah",
            title="Test 4: Customdata"
        )
        test_fig4.data[0].customdata = test_data[['jumlah']].values
        test_fig4.update_traces(
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>Jumlah: %{customdata[0]:,}<extra></extra>"
        )
        st.plotly_chart(test_fig4, use_container_width=True)
        st.success("Test 4: Customdata created successfully!")
        st.write(f"**Customdata shape:** {test_fig4.data[0].customdata.shape}")
        st.write(f"**Customdata sample:** {test_fig4.data[0].customdata[:3].flatten()}")
    except Exception as e:
        st.error(f"Error creating test 4: {e}")

st.plotly_chart(fig1, use_container_width=True)

# Alternative 2: Show data table below treemap
st.subheader("📊 Data Detail - OPD → Eselon")
st.info("💡 **Tips**: Jika nilai tidak muncul di treemap, gunakan tabel detail di bawah untuk melihat data lengkap dengan jumlah dan persentase.")
with st.expander("Lihat Data Detail", expanded=False):
    # Show aggregated data in table format
    display_data = agg1.copy()
    display_data = display_data.sort_values('jumlah', ascending=False)
    display_data['persentase'] = (display_data['jumlah'] / display_data['jumlah'].sum() * 100).round(2)
    display_data = display_data.rename(columns={
        COL_OPD: 'OPD',
        COL_ESELON: 'Eselon',
        'jumlah': 'Jumlah',
        'persentase': 'Persentase (%)'
    })
    
    st.dataframe(display_data, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pegawai", f"{display_data['Jumlah'].sum():,}")
    with col2:
        st.metric("Jumlah OPD", f"{display_data['OPD'].nunique():,}")
    with col3:
        st.metric("Jumlah Eselon", f"{display_data['Eselon'].nunique():,}")
    with col4:
        st.metric("Rata-rata per OPD", f"{display_data['Jumlah'].mean():.1f}")

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

logger.info(f"Treemap 2 data shape: {agg2.shape}")
logger.info(f"Treemap 2 columns: {list(agg2.columns)}")
logger.info(f"Path hierarchy: {path_hierarchy}")

# Create treemap with simple approach
fig2 = px.treemap(
    agg2,
    path=path_hierarchy,
    values="jumlah",
    title="Treemap — OPD → Eselon → Jabatan"
)
fig2.update_layout(margin=dict(t=40,l=0,r=0,b=0))

# Show values directly on treemap
fig2.update_traces(
    textinfo="label+value",
    texttemplate="%{label}<br>%{value}",
    textfont_size=10,
    textposition="middle center"
)

logger.info("Treemap 2 created with simple approach")

st.plotly_chart(fig2, use_container_width=True)

# Data table for Treemap 2
st.subheader("📊 Data Detail - OPD → Eselon → Jabatan")
st.info("💡 **Tips**: Tabel ini menampilkan data jabatan lengkap dengan jumlah pegawai dan persentase.")
with st.expander("Lihat Data Detail Jabatan", expanded=False):
    display_data2 = agg2.copy()
    display_data2 = display_data2.sort_values('jumlah', ascending=False)
    display_data2['persentase'] = (display_data2['jumlah'] / display_data2['jumlah'].sum() * 100).round(2)
    display_data2 = display_data2.rename(columns={
        COL_OPD: 'OPD',
        COL_ESELON: 'Eselon',
        COL_JAB: 'Jabatan',
        'jumlah': 'Jumlah',
        'persentase': 'Persentase (%)'
    })
    
    st.dataframe(display_data2.head(20), use_container_width=True)
    
    # Summary for Treemap 2
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jabatan", f"{display_data2['Jumlah'].sum():,}")
    with col2:
        st.metric("Jumlah Jabatan Unik", f"{display_data2['Jabatan'].nunique():,}")
    with col3:
        st.metric("Rata-rata per Jabatan", f"{display_data2['Jumlah'].mean():.1f}")

# ======================
# 8. Treemap Tambahan: OPD → Golongan
# ======================
st.subheader("Treemap 3: OPD → Golongan")
agg3 = (dff.groupby([COL_OPD, COL_GOL], dropna=False).size().reset_index(name="jumlah"))

for col in [COL_OPD, COL_GOL]:
    agg3[col] = agg3[col].fillna("Tidak Diketahui")
    agg3[col] = agg3[col].replace("", "Tidak Diketahui")

logger.info(f"Treemap 3 data shape: {agg3.shape}")
logger.info(f"Treemap 3 columns: {list(agg3.columns)}")

# Create treemap with simple approach
fig3 = px.treemap(
    agg3,
    path=[COL_OPD, COL_GOL],
    values="jumlah",
    title="Treemap — OPD → Golongan"
)
fig3.update_layout(margin=dict(t=40,l=0,r=0,b=0))

# Show values directly on treemap
fig3.update_traces(
    textinfo="label+value",
    texttemplate="%{label}<br>%{value}",
    textfont_size=12,
    textposition="middle center"
)

logger.info("Treemap 3 created with simple approach")

st.plotly_chart(fig3, use_container_width=True)

# Data table for Treemap 3
st.subheader("📊 Data Detail - OPD → Golongan")
st.info("💡 **Tips**: Tabel ini menampilkan distribusi pegawai berdasarkan OPD dan golongan dengan persentase.")
with st.expander("Lihat Data Detail Golongan", expanded=False):
    display_data3 = agg3.copy()
    display_data3 = display_data3.sort_values('jumlah', ascending=False)
    display_data3['persentase'] = (display_data3['jumlah'] / display_data3['jumlah'].sum() * 100).round(2)
    display_data3 = display_data3.rename(columns={
        COL_OPD: 'OPD',
        COL_GOL: 'Golongan',
        'jumlah': 'Jumlah',
        'persentase': 'Persentase (%)'
    })
    
    st.dataframe(display_data3, use_container_width=True)
    
    # Summary for Treemap 3
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pegawai", f"{display_data3['Jumlah'].sum():,}")
    with col2:
        st.metric("Jumlah Golongan", f"{display_data3['Golongan'].nunique():,}")
    with col3:
        st.metric("Rata-rata per Golongan", f"{display_data3['Jumlah'].mean():.1f}")

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
