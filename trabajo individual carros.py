import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ---------------------------------------------------------
# 1. CONFIGURACIÓN Y PALETA MINIMALISTA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Mexico Automotive Intelligence (2016–2026)", layout="wide"
)

AZUL = "#1f77b4"
AZUL_MEDIO = "#5b9bd5"
AZUL_CLARO = "#9dc3e6"
GRIS_OSCURO = "#4d4d4d"
GRIS_MEDIO = "#8c8c8c"
GRIS_CLARO = "#d9d9d9"


def estilo_limpio(ax, bottom=False):
  sns.despine(ax=ax, left=True, right=True, top=True, bottom=not bottom)
  ax.tick_params(left=False, bottom=bottom, colors=GRIS_OSCURO, labelsize=9)


# ---------------------------------------------------------
# 2. CARGA Y LIMPIEZA DE DATOS (2016 - 2026)
# ---------------------------------------------------------
@st.cache_data
def cargar_datos():
  archivos = sorted(glob.glob("raiavl_venta_mensual_tr_cifra_*.csv"))
  df = pd.concat([pd.read_csv(f) for f in archivos], ignore_index=True)

  for col in ["MARCA", "MODELO", "SEGMENTO", "ORIGEN", "TIPO"]:
    df[col] = df[col].astype(str).str.strip()

  homologar = {
      "Chrysler": "Stellantis",
      "Fiat": "Stellantis",
      "Alfa Romeo": "Stellantis",
      "Peugeot": "Stellantis",
      "MG": "MG Motor",
  }
  df["MARCA_LIMPIA"] = df["MARCA"].replace(homologar)
  df["FECHA"] = pd.to_datetime(
      df["ANIO"].astype(str) + "-" + df["ID_MES"].astype(str).str.zfill(2) + "-01"
  )
  return df


df = cargar_datos()

# ---------------------------------------------------------
# 3. BARRA LATERAL: NAVEGACIÓN POR CAPÍTULOS Y FILTROS
# ---------------------------------------------------------
st.sidebar.title("Navigation & Filters")

pagina = st.sidebar.radio(
    "Select Story Chapter:",
    [
        "Chapter 1 · Industry & Market Overview",
        "Chapter 2 · Nissan vs. Key Competitors",
        "Chapter 3 · Vehicle Segments (Luxury, SUVs, Vans)",
        "Chapter 4 · Domestic vs. Imported & Tariffs",
    ],
)

st.sidebar.divider()
st.sidebar.subheader("Global Filters")

anios = st.sidebar.slider(
    "Year Window",
    int(df["ANIO"].min()),
    int(df["ANIO"].max()),
    (2016, 2026),
)

segmentos_disp = sorted(df["SEGMENTO"].unique())
seg_sel = st.sidebar.multiselect(
    "Segments", segmentos_disp, default=segmentos_disp
)

origenes_disp = sorted(df["ORIGEN"].unique())
orig_sel = st.sidebar.multiselect("Origin", origenes_disp, default=origenes_disp)

df_f = df[
    (df["ANIO"].between(anios[0], anios[1]))
    & (df["SEGMENTO"].isin(seg_sel))
    & (df["ORIGEN"].isin(orig_sel))
]

# ---------------------------------------------------------
# 4. ENCABEZADO EJECUTIVO FIJO
# ---------------------------------------------------------
st.title("The Emerging Stories of Mexico's Automotive Industry")
st.caption(
    "**Role:** Automotive Market Strategy Consultant | **Stakeholders:**"
    " Commercial & Product Planning Leadership | **Data:** INEGI RAIAVL"
    f" ({anios[0]}–{anios[1]})"
)

total_u = df_f["UNI_VEH"].sum()
nissan_u = df_f[df_f["MARCA_LIMPIA"] == "Nissan"]["UNI_VEH"].sum()
nac_u = df_f[df_f["ORIGEN"] == "NACIONAL"]["UNI_VEH"].sum()
suv_u = df_f[df_f["SEGMENTO"] == "SUV's"]["UNI_VEH"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Retail Sales", f"{total_u:,.0f}")
k2.metric(
    "Nissan Market Share",
    f"{(nissan_u/total_u*100 if total_u else 0):.1f}%",
    f"{nissan_u:,.0f} units",
)
k3.metric(
    "SUV Segment Share",
    f"{(suv_u/total_u*100 if total_u else 0):.1f}%",
    f"{suv_u:,.0f} units",
)
k4.metric(
    "Domestic Production Share",
    f"{(nac_u/total_u*100 if total_u else 0):.1f}%",
    f"{nac_u:,.0f} units",
)

st.divider()

# =========================================================
# CHAPTER 1: INDUSTRY & MARKET OVERVIEW (CHARTS 1 - 4)
# =========================================================
if pagina.startswith("Chapter 1"):
  st.header("Chapter 1 · A Decade of Shocks, Seasonality & Market Power")
  st.write(
      "Understanding the macro trajectory of Mexico's light-vehicle retail"
      " market from 2016 to 2026 before diving into brand and segment battles."
  )

  # --- CHART 1: Evolución 10 años ---
  c1, c2 = st.columns([1.2, 1])
  with c1:
    st.subheader("1.1 Decade Trajectory & Macro Shocks")
    anual_mkt = df_f.groupby("ANIO", as_index=False)["UNI_VEH"].sum()
    anual_nis = (
        df_f[df_f["MARCA_LIMPIA"] == "Nissan"]
        .groupby("ANIO", as_index=False)["UNI_VEH"]
        .sum()
    )

    fig1, ax1 = plt.subplots(figsize=(6.8, 3.8))
    ax1.fill_between(
        anual_mkt["ANIO"], anual_mkt["UNI_VEH"], color=AZUL_CLARO, alpha=0.22
    )
    ax1.plot(
        anual_mkt["ANIO"],
        anual_mkt["UNI_VEH"],
        color=GRIS_MEDIO,
        lw=1.8,
        marker="o",
        ms=4,
    )
    ax1.plot(
        anual_nis["ANIO"],
        anual_nis["UNI_VEH"],
        color=AZUL,
        lw=2.6,
        marker="o",
        ms=4.5,
    )

    if len(anual_mkt) > 0:
      ua = anual_mkt["ANIO"].iloc[-1]
      ax1.text(
          ua + 0.15,
          anual_mkt["UNI_VEH"].iloc[-1],
          f"Market\n({anual_mkt['UNI_VEH'].iloc[-1]/1e6:.2f}M)",
          va="center",
          fontsize=8.5,
          fontweight="bold",
          color=GRIS_OSCURO,
      )
    if len(anual_nis) > 0:
      ax1.text(
          ua + 0.15,
          anual_nis["UNI_VEH"].iloc[-1],
          f"Nissan\n({anual_nis['UNI_VEH'].iloc[-1]/1000:.0f}k)",
          va="center",
          fontsize=8.5,
          fontweight="bold",
          color=AZUL,
      )

    if anios[0] <= 2020 and anios[1] >= 2022:
      ax1.axvspan(2020, 2022, color=GRIS_CLARO, alpha=0.35, zorder=0)
      ax1.text(
          2021,
          anual_mkt["UNI_VEH"].max() * 0.94,
          "2020–22: COVID & Chips",
          ha="center",
          fontsize=8,
          fontweight="bold",
          color=GRIS_OSCURO,
      )
    if anios[0] <= 2026 <= anios[1]:
      ax1.axvline(2026, color=AZUL, ls=":", lw=1.2)
      ax1.text(
          2025.85,
          anual_mkt["UNI_VEH"].max() * 0.62,
          "Jan 2026\nTariffs",
          ha="right",
          fontsize=8,
          fontweight="bold",
          color=AZUL,
      )

    ax1.set_title(
        "Total industry vs. Nissan (2026 = Jan–Oct)",
        loc="left",
        fontsize=11,
        fontweight="bold",
        color=AZUL,
    )
    ax1.set_xlim(anios[0] - 0.3, anios[1] + 1.4)
    ax1.set_ylim(
        0, anual_mkt["UNI_VEH"].max() * 1.12 if len(anual_mkt) else 100
    )
    ax1.yaxis.set_major_formatter(
        plt.FuncFormatter(
            lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1000:.0f}k"
        )
    )
    ax1.grid(axis="y", ls="--", alpha=0.25)
    estilo_limpio(ax1, bottom=True)
    st.pyplot(fig1)

  # --- CHART 2: Top 10 Marcas Concentración ---
  with c2:
    st.subheader("1.2 Market Concentration (Top 10 Brands)")
    t_marcas = (
        df_f.groupby("MARCA_LIMPIA", as_index=False)["UNI_VEH"]
        .sum()
        .sort_values("UNI_VEH", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    t_marcas["Share"] = (
        t_marcas["UNI_VEH"] / total_u * 100 if total_u > 0 else 0
    )
    top5_s = t_marcas["Share"].head(5).sum()

    col_b = ([AZUL] + [AZUL_CLARO] * 4 + [GRIS_CLARO] * 5)[: len(t_marcas)]
    fig2, ax2 = plt.subplots(figsize=(6, 3.8))
    sns.barplot(
        data=t_marcas,
        x="Share",
        y="MARCA_LIMPIA",
        hue="MARCA_LIMPIA",
        palette=dict(zip(t_marcas["MARCA_LIMPIA"], col_b)),
        legend=False,
        ax=ax2,
    )

    for i, r in t_marcas.iterrows():
      v = r["Share"]
      if i < 5:
        ax2.text(
            v - 0.3,
            i,
            f"{v:.1f}%",
            ha="right",
            va="center",
            color="white",
            fontsize=8,
            fontweight="bold",
        )
      else:
        ax2.text(
            v + 0.25,
            i,
            f"{v:.1f}%",
            ha="left",
            va="center",
            color=GRIS_OSCURO,
            fontsize=8,
        )

    ax2.set_title(
        f"Top 5 brands capture {top5_s:.0f}% of total sales",
        loc="left",
        fontsize=11,
        fontweight="bold",
        color=AZUL,
    )
    ax2.set_xlim(0, t_marcas["Share"].max() * 1.18 if len(t_marcas) else 20)
    ax2.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax2)
    st.pyplot(fig2)

  st.divider()
  c3, c4 = st.columns(2)

  # --- CHART 3: Estacionalidad Mensual (2026 vs Promedio Histórico) ---
  with c3:
    st.subheader("1.3 Monthly Seasonality: 2026 vs. Historical Average")
    meses_lbl = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    hist_mes = (
        df[df["ANIO"] < 2026].groupby("ID_MES", as_index=False)["UNI_VEH"].mean()
    )
    # Sumar por mes-año primero para sacar promedio mensual real
    hist_mes = (
        df[
            (df["ANIO"] < 2026)
            & (df["SEGMENTO"].isin(seg_sel))
            & (df["ORIGEN"].isin(orig_sel))
        ]
        .groupby(["ANIO", "ID_MES"], as_index=False)["UNI_VEH"]
        .sum()
        .groupby("ID_MES", as_index=False)["UNI_VEH"]
        .mean()
    )
    m_2026 = (
        df[
            (df["ANIO"] == 2026)
            & (df["SEGMENTO"].isin(seg_sel))
            & (df["ORIGEN"].isin(orig_sel))
        ]
        .groupby("ID_MES", as_index=False)["UNI_VEH"]
        .sum()
    )

    fig3, ax3 = plt.subplots(figsize=(6, 3.6))
    ax3.plot(
        hist_mes["ID_MES"],
        hist_mes["UNI_VEH"],
        color=GRIS_MEDIO,
        ls="--",
        lw=1.8,
        marker="o",
        ms=3.5,
        label="2016–2025 Monthly Avg",
    )
    ax3.plot(
        m_2026["ID_MES"],
        m_2026["UNI_VEH"],
        color=AZUL,
        lw=2.5,
        marker="o",
        ms=4.5,
        label="2026 Actual (Jan–Oct)",
    )

    ax3.set_title(
        "2026 sales outperform historical monthly averages",
        loc="left",
        fontsize=11,
        fontweight="bold",
        color=AZUL,
    )
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(meses_lbl)
    ax3.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}k")
    )
    ax3.grid(axis="y", ls="--", alpha=0.25)
    ax3.legend(frameon=False, fontsize=8.5, loc="upper left")
    estilo_limpio(ax3, bottom=True)
    st.pyplot(fig3)

  # --- CHART 4: Cambio en Market Share (2016 vs 2026) ---
  with c4:
    st.subheader("1.4 Winners & Losers of the Decade (Share Shift)")
    s16 = df[
        (df["ANIO"] == 2016)
        & (df["SEGMENTO"].isin(seg_sel))
        & (df["ORIGEN"].isin(orig_sel))
    ].groupby("MARCA_LIMPIA")["UNI_VEH"].sum()
    s16 = s16 / s16.sum() * 100
    s26 = df[
        (df["ANIO"] == 2026)
        & (df["SEGMENTO"].isin(seg_sel))
        & (df["ORIGEN"].isin(orig_sel))
    ].groupby("MARCA_LIMPIA")["UNI_VEH"].sum()
    s26 = s26 / s26.sum() * 100

    diff = (s26 - s16).dropna().sort_values()
    extremos = pd.concat([diff.head(4), diff.tail(4)]).reset_index()
    extremos.columns = ["Brand", "Change"]

    col_d = [AZUL if x > 0 else GRIS_CLARO for x in extremos["Change"]]
    fig4, ax4 = plt.subplots(figsize=(6, 3.6))
    sns.barplot(
        data=extremos,
        x="Change",
        y="Brand",
        hue="Brand",
        palette=dict(zip(extremos["Brand"], col_d)),
        legend=False,
        ax=ax4,
    )
    ax4.axvline(0, color=GRIS_OSCURO, lw=0.8)

    for i, r in extremos.iterrows():
      v = r["Change"]
      ax4.text(
          v + (0.2 if v >= 0 else -0.2),
          i,
          f"{v:+.1f} pp",
          va="center",
          ha="left" if v >= 0 else "right",
          fontsize=8,
          color=GRIS_OSCURO,
          fontweight="bold" if v > 0 else "normal",
      )

    ax4.set_title(
        "Market share change: 2026 vs. 2016 (percentage points)",
        loc="left",
        fontsize=11,
        fontweight="bold",
        color=AZUL,
    )
    ax4.set_xlim(
        extremos["Change"].min() * 1.35, extremos["Change"].max() * 1.35
    )
    ax4.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax4)
    st.pyplot(fig4)

# =========================================================
# CHAPTER 2: NISSAN VS. KEY COMPETITORS (CHARTS 5 - 8)
# =========================================================
elif pagina.startswith("Chapter 2"):
  st.header("Chapter 2 · Competitive Deep-Dive: Nissan vs. Top Rivals")
  st.write(
      "Evaluating how Nissan defends its #1 position against General Motors,"
      " Volkswagen, Toyota, and KIA, and analyzing product portfolio"
      " concentration."
  )

  top5_list = (
      df_f.groupby("MARCA_LIMPIA")["UNI_VEH"]
      .sum()
      .sort_values(ascending=False)
      .head(5)
      .index.tolist()
  )

  c1, c2 = st.columns(2)

  # --- CHART 5: Evolución de Market Share del Top 5 ---
  with c1:
    st.subheader("2.1 Market Share Trajectory of Top 5 Brands (%)")
    anual_tot = df_f.groupby("ANIO")["UNI_VEH"].sum()
    sh_top5 = (
        df_f[df_f["MARCA_LIMPIA"].isin(top5_list)]
        .groupby(["ANIO", "MARCA_LIMPIA"])["UNI_VEH"]
        .sum()
        .unstack(fill_value=0)
    )
    sh_top5 = sh_top5.div(anual_tot, axis=0) * 100

    fig5, ax5 = plt.subplots(figsize=(6.2, 3.8))
    pal5 = [AZUL, AZUL_MEDIO, "#8faadc", GRIS_MEDIO, GRIS_CLARO]
    for idx, m in enumerate(top5_list):
      if m in sh_top5.columns:
        ax5.plot(
            sh_top5.index,
            sh_top5[m],
            color=pal5[idx],
            lw=2.6 if idx == 0 else 1.5,
            marker="o",
            ms=3.5,
            label=m,
        )

    ax5.set_title(
        "Nissan holds >17% share while rivals cluster around 7–13%",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax5.set_ylabel("Market Share (%)", fontsize=8.5, color=GRIS_OSCURO)
    ax5.legend(frameon=False, ncol=3, fontsize=8, loc="upper right")
    ax5.grid(axis="y", ls="--", alpha=0.25)
    estilo_limpio(ax5, bottom=True)
    st.pyplot(fig5)

  # --- CHART 6: Brecha de unidades respecto a Nissan ---
  with c2:
    st.subheader("2.2 Volume Gap Against the #1 Leader")
    top8_vol = (
        df_f.groupby("MARCA_LIMPIA", as_index=False)["UNI_VEH"]
        .sum()
        .sort_values("UNI_VEH", ascending=False)
        .head(8)
        .reset_index(drop=True)
    )
    lider_v = top8_vol["UNI_VEH"].iloc[0] if len(top8_vol) else 0
    top8_vol["Gap"] = top8_vol["UNI_VEH"] - lider_v

    fig6, ax6 = plt.subplots(figsize=(6.2, 3.8))
    col_g = [AZUL if i == 0 else GRIS_CLARO for i in range(len(top8_vol))]
    sns.barplot(
        data=top8_vol,
        x="UNI_VEH",
        y="MARCA_LIMPIA",
        hue="MARCA_LIMPIA",
        palette=dict(zip(top8_vol["MARCA_LIMPIA"], col_g)),
        legend=False,
        ax=ax6,
    )

    for i, r in top8_vol.iterrows():
      if i == 0:
        ax6.text(
            r["UNI_VEH"] - (lider_v * 0.03),
            i,
            f"{r['UNI_VEH']/1000:,.0f}k (Leader)",
            ha="right",
            va="center",
            color="white",
            fontsize=8,
            fontweight="bold",
        )
      else:
        ax6.text(
            r["UNI_VEH"] + (lider_v * 0.02),
            i,
            f"{r['UNI_VEH']/1000:,.0f}k ({r['Gap']/1000:,.0f}k)",
            ha="left",
            va="center",
            color=GRIS_OSCURO,
            fontsize=8,
        )

    ax6.set_title(
        "Unit difference vs. #1 brand in selected period",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax6.set_xlim(0, lider_v * 1.28)
    ax6.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax6)
    st.pyplot(fig6)

  st.divider()
  c3, c4 = st.columns(2)

  # --- CHART 7: Motores de Nissan (Top Modelos) ---
  with c3:
    st.subheader("2.3 Inside Nissan: Top Selling Models")
    nis_m = (
        df_f[df_f["MARCA_LIMPIA"] == "Nissan"]
        .groupby("MODELO", as_index=False)["UNI_VEH"]
        .sum()
        .sort_values("UNI_VEH", ascending=False)
        .head(8)
        .reset_index(drop=True)
    )
    nis_m["Share"] = nis_m["UNI_VEH"] / nissan_u * 100 if nissan_u > 0 else 0
    top2_nis = nis_m["Share"].head(2).sum()

    col_nm = ([AZUL, AZUL] + [AZUL_CLARO] * 2 + [GRIS_CLARO] * 4)[: len(nis_m)]
    fig7, ax7 = plt.subplots(figsize=(6.2, 3.8))
    sns.barplot(
        data=nis_m,
        x="UNI_VEH",
        y="MODELO",
        hue="MODELO",
        palette=dict(zip(nis_m["MODELO"], col_nm)),
        legend=False,
        ax=ax7,
    )

    for i, r in nis_m.iterrows():
      v, p = r["UNI_VEH"], r["Share"]
      if i < 2:
        ax7.text(
            v - (nis_m["UNI_VEH"].max() * 0.03),
            i,
            f"{v/1000:,.0f}k ({p:.0f}%)",
            ha="right",
            va="center",
            color="white",
            fontsize=8,
            fontweight="bold",
        )
      else:
        ax7.text(
            v + (nis_m["UNI_VEH"].max() * 0.02),
            i,
            f"{v/1000:,.0f}k ({p:.0f}%)",
            ha="left",
            va="center",
            color=GRIS_OSCURO,
            fontsize=8,
        )

    ax7.set_title(
        f"Versa & NP300 drive {top2_nis:.0f}% of Nissan's volume",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax7.set_xlim(0, nis_m["UNI_VEH"].max() * 1.25 if len(nis_m) else 100)
    ax7.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax7)
    st.pyplot(fig7)

  # --- CHART 8: Riesgo de concentración por marca (Top 2 modelos % por marca) ---
  with c4:
    st.subheader("2.4 Portfolio Risk: Top-2 Model Dependency")
    dep_rows = []
    for m in top5_list:
      sub_m = df_f[df_f["MARCA_LIMPIA"] == m]
      tot_m = sub_m["UNI_VEH"].sum()
      top2_m = sub_m.groupby("MODELO")["UNI_VEH"].sum().nlargest(2).sum()
      dep_rows.append(
          {"Brand": m, "Top2_Pct": (top2_m / tot_m * 100) if tot_m > 0 else 0}
      )
    dep_df = pd.DataFrame(dep_rows).sort_values("Top2_Pct", ascending=False)

    col_dep = [AZUL if b == "Nissan" else GRIS_CLARO for b in dep_df["Brand"]]
    fig8, ax8 = plt.subplots(figsize=(6.2, 3.8))
    sns.barplot(
        data=dep_df,
        x="Top2_Pct",
        y="Brand",
        hue="Brand",
        palette=dict(zip(dep_df["Brand"], col_dep)),
        legend=False,
        ax=ax8,
    )

    for i, r in dep_df.reset_index(drop=True).iterrows():
      ax8.text(
          r["Top2_Pct"] + 1,
          i,
          f"{r['Top2_Pct']:.1f}%",
          va="center",
          fontsize=8.5,
          fontweight="bold" if r["Brand"] == "Nissan" else "normal",
          color=GRIS_OSCURO,
      )

    ax8.set_title(
        "Share of brand sales coming from its 2 best-selling models",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax8.set_xlim(0, 100)
    ax8.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax8)
    st.pyplot(fig8)

# =========================================================
# CHAPTER 3: VEHICLE SEGMENTS & TIER SHIFTS (CHARTS 9 - 12)
# =========================================================
elif pagina.startswith("Chapter 3"):
  st.header("Chapter 3 · Vehicle Tiers: SUVs, Luxury & Minivans vs. Mass Cars")
  st.write(
      "Comparing how consumer preferences are shifting across vehicle types and"
      " identifying who wins in specialized tiers like De Lujo and Minivans."
  )

  c1, c2 = st.columns(2)

  # --- CHART 9: Mix de Segmentos ---
  with c1:
    st.subheader("3.1 Total Volume & Share by Segment")
    seg_df = (
        df_f.groupby("SEGMENTO", as_index=False)["UNI_VEH"]
        .sum()
        .sort_values("UNI_VEH", ascending=False)
        .reset_index(drop=True)
    )
    seg_df["Share"] = seg_df["UNI_VEH"] / total_u * 100 if total_u > 0 else 0

    col_s = [
        AZUL if s in ["SUV's", "De Lujo", "Minivans"] else GRIS_CLARO
        for s in seg_df["SEGMENTO"]
    ]
    fig9, ax9 = plt.subplots(figsize=(6.2, 3.8))
    sns.barplot(
        data=seg_df,
        x="UNI_VEH",
        y="SEGMENTO",
        hue="SEGMENTO",
        palette=dict(zip(seg_df["SEGMENTO"], col_s)),
        legend=False,
        ax=ax9,
    )

    for i, r in seg_df.iterrows():
      ax9.text(
          r["UNI_VEH"] + (seg_df["UNI_VEH"].max() * 0.02),
          i,
          f"{r['UNI_VEH']/1000:,.0f}k ({r['Share']:.1f}%)",
          va="center",
          fontsize=8,
          color=GRIS_OSCURO,
      )

    ax9.set_title(
        "SUVs and Compact cars dominate overall volume",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax9.set_xlim(0, seg_df["UNI_VEH"].max() * 1.32 if len(seg_df) else 100)
    ax9.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax9)
    st.pyplot(fig9)

  # --- CHART 10: La Revolución SUV vs Compactos/Subcompactos ---
  with c2:
    st.subheader("3.2 Structural Shift: SUVs vs. Sedans (2016–2026)")
    cats_comp = ["SUV's", "Compactos", "Subcompactos"]
    piv_seg = (
        df_f[df_f["SEGMENTO"].isin(cats_comp)]
        .groupby(["ANIO", "SEGMENTO"])["UNI_VEH"]
        .sum()
        .unstack(fill_value=0)
    )
    tot_an = df_f.groupby("ANIO")["UNI_VEH"].sum()
    piv_pct = piv_seg.div(tot_an, axis=0) * 100

    fig10, ax10 = plt.subplots(figsize=(6.2, 3.8))
    col_c = {"SUV's": AZUL, "Compactos": GRIS_MEDIO, "Subcompactos": GRIS_CLARO}
    for cat in cats_comp:
      if cat in piv_pct.columns:
        ax10.plot(
            piv_pct.index,
            piv_pct[cat],
            color=col_c[cat],
            lw=2.6 if cat == "SUV's" else 1.8,
            marker="o",
            ms=4,
            label=cat,
        )

    ax10.set_title(
        "SUV market share surged while Subcompact cars contracted",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax10.set_ylabel("Share of Total Sales (%)", fontsize=8.5, color=GRIS_OSCURO)
    ax10.legend(frameon=False, fontsize=8.5)
    ax10.grid(axis="y", ls="--", alpha=0.25)
    estilo_limpio(ax10, bottom=True)
    st.pyplot(fig10)

  st.divider()
  c3, c4 = st.columns([1, 1.3])

  # --- CHART 11: Nichos especializados (De Lujo vs Minivans vs Pick Ups) ---
  with c3:
    st.subheader("3.3 High-Value Tiers: Luxury, Minivans & Pick Ups")
    nichos = ["Pick Ups", "De Lujo", "Minivans"]
    piv_n = (
        df_f[df_f["SEGMENTO"].isin(nichos)]
        .groupby(["ANIO", "SEGMENTO"])["UNI_VEH"]
        .sum()
        .unstack(fill_value=0)
    )

    fig11, ax11 = plt.subplots(figsize=(5.5, 3.8))
    col_n = {"Pick Ups": AZUL, "De Lujo": AZUL_MEDIO, "Minivans": GRIS_MEDIO}
    for n in nichos:
      if n in piv_n.columns:
        ax11.plot(
            piv_n.index, piv_n[n], color=col_n[n], lw=2.1, marker="o", ms=3.5, label=n
        )

    ax11.set_title(
        "Annual unit volume in specialized tiers",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax11.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}k")
    )
    ax11.legend(frameon=False, fontsize=8.5)
    ax11.grid(axis="y", ls="--", alpha=0.25)
    estilo_limpio(ax11, bottom=True)
    st.pyplot(fig11)

  # --- CHART 12: Explorador interactivo por segmento ---
  with c4:
    st.subheader("3.4 Category Leaders (Interactive Selector)")
    seg_pick = st.selectbox(
        "Choose a segment to inspect its top models:",
        options=segmentos_disp,
        index=segmentos_disp.index("De Lujo")
        if "De Lujo" in segmentos_disp
        else 0,
    )
    sub_cat = df_f[df_f["SEGMENTO"] == seg_pick]
    tot_cat = sub_cat["UNI_VEH"].sum()
    top_m_cat = (
        sub_cat.groupby(["MARCA_LIMPIA", "MODELO"], as_index=False)["UNI_VEH"]
        .sum()
        .sort_values("UNI_VEH", ascending=False)
        .head(7)
        .reset_index(drop=True)
    )
    top_m_cat["Label"] = top_m_cat["MARCA_LIMPIA"] + " · " + top_m_cat["MODELO"]

    col_mc = ([AZUL] + [AZUL_CLARO] * 2 + [GRIS_CLARO] * 4)[: len(top_m_cat)]
    fig12, ax12 = plt.subplots(figsize=(6.5, 3.3))
    sns.barplot(
        data=top_m_cat,
        x="UNI_VEH",
        y="Label",
        hue="Label",
        palette=dict(zip(top_m_cat["Label"], col_mc)),
        legend=False,
        ax=ax12,
    )

    for i, r in top_m_cat.iterrows():
      pct_c = r["UNI_VEH"] / tot_cat * 100 if tot_cat > 0 else 0
      ax12.text(
          r["UNI_VEH"] + (top_m_cat["UNI_VEH"].max() * 0.02),
          i,
          f"{r['UNI_VEH']:,.0f} ({pct_c:.1f}%)",
          va="center",
          fontsize=8,
          color=GRIS_OSCURO,
      )

    ax12.set_title(
        f"Best-selling models in '{seg_pick}' (Total: {tot_cat:,.0f} units)",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax12.set_xlim(
        0, top_m_cat["UNI_VEH"].max() * 1.32 if len(top_m_cat) else 100
    )
    ax12.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax12)
    st.pyplot(fig12)

# =========================================================
# CHAPTER 4: DOMESTIC VS. IMPORTED & TARIFF EXPOSURE (CHARTS 13 - 16)
# =========================================================
else:
  st.header("Chapter 4 · Made in Mexico vs. Imported: Tariff Risk Exposure")
  st.write(
      "Analyzing domestic vs. foreign sourcing across brands and vehicle tiers"
      " to evaluate vulnerability to the January 2026 tariff adjustments."
  )

  c1, c2 = st.columns(2)

  # --- CHART 13: Evolución Nacional vs Importado ---
  with c1:
    st.subheader("4.1 Domestic vs. Imported Mix Over Time (%)")
    orig_an = (
        df_f.groupby(["ANIO", "ORIGEN"])["UNI_VEH"].sum().unstack(fill_value=0)
    )
    orig_pct = orig_an.div(orig_an.sum(axis=1), axis=0) * 100

    fig13, ax13 = plt.subplots(figsize=(6.2, 3.8))
    if "IMPORTADO" in orig_pct.columns:
      ax13.plot(
          orig_pct.index,
          orig_pct["IMPORTADO"],
          color=AZUL,
          lw=2.5,
          marker="o",
          ms=4,
          label="Imported (%)",
      )
    if "NACIONAL" in orig_pct.columns:
      ax13.plot(
          orig_pct.index,
          orig_pct["NACIONAL"],
          color=GRIS_MEDIO,
          lw=2,
          marker="o",
          ms=4,
          label="Domestic / Made in Mexico (%)",
      )

    ax13.set_title(
        "Over 60% of vehicles sold in Mexico are imported",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax13.set_ylim(0, 100)
    ax13.set_ylabel("Share of Retail Sales (%)", fontsize=8.5, color=GRIS_OSCURO)
    ax13.legend(frameon=False, fontsize=8.5)
    ax13.grid(axis="y", ls="--", alpha=0.25)
    estilo_limpio(ax13, bottom=True)
    st.pyplot(fig13)

  # --- CHART 14: Exposición a Importaciones por Marca (Top 10) ---
  with c2:
    st.subheader("4.2 Tariff Exposure: Imported Share by Top 10 Brands")
    top10_b = (
        df_f.groupby("MARCA_LIMPIA")["UNI_VEH"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )
    b_orig = (
        df_f[df_f["MARCA_LIMPIA"].isin(top10_b)]
        .groupby(["MARCA_LIMPIA", "ORIGEN"])["UNI_VEH"]
        .sum()
        .unstack(fill_value=0)
    )
    b_orig["Imp_Pct"] = (
        (b_orig.get("IMPORTADO", 0) / b_orig.sum(axis=1) * 100)
        if len(b_orig)
        else 0
    )
    b_orig = b_orig.sort_values("Imp_Pct", ascending=False).reset_index()

    col_imp = [
        AZUL if m == "Nissan" else (AZUL_CLARO if p > 70 else GRIS_CLARO)
        for m, p in zip(b_orig["MARCA_LIMPIA"], b_orig["Imp_Pct"])
    ]
    fig14, ax14 = plt.subplots(figsize=(6.2, 3.8))
    sns.barplot(
        data=b_orig,
        x="Imp_Pct",
        y="MARCA_LIMPIA",
        hue="MARCA_LIMPIA",
        palette=dict(zip(b_orig["MARCA_LIMPIA"], col_imp)),
        legend=False,
        ax=ax14,
    )

    for i, r in b_orig.iterrows():
      ax14.text(
          r["Imp_Pct"] + 1.5,
          i,
          f"{r['Imp_Pct']:.0f}%",
          va="center",
          fontsize=8,
          color=GRIS_OSCURO,
          fontweight="bold" if r["MARCA_LIMPIA"] == "Nissan" else "normal",
      )

    ax14.set_title(
        "Imported share of retail sales (Nissan highlighted)",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax14.set_xlim(0, 115)
    ax14.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax14)
    st.pyplot(fig14)

  st.divider()
  c3, c4 = st.columns(2)

  # --- CHART 15: Porcentaje Importado por Segmento ---
  with c3:
    st.subheader("4.3 Imported Reliance by Vehicle Segment")
    s_orig = df_f.groupby(["SEGMENTO", "ORIGEN"])["UNI_VEH"].sum().unstack(fill_value=0)
    s_orig["Imp_Pct"] = s_orig.get("IMPORTADO", 0) / s_orig.sum(axis=1) * 100
    s_orig = s_orig.sort_values("Imp_Pct", ascending=False).reset_index()

    col_so = [
        AZUL if s in ["De Lujo", "Minivans", "SUV's"] else GRIS_CLARO
        for s in s_orig["SEGMENTO"]
    ]
    fig15, ax15 = plt.subplots(figsize=(6.2, 3.8))
    sns.barplot(
        data=s_orig,
        x="Imp_Pct",
        y="SEGMENTO",
        hue="SEGMENTO",
        palette=dict(zip(s_orig["SEGMENTO"], col_so)),
        legend=False,
        ax=ax15,
    )

    for i, r in s_orig.iterrows():
      ax15.text(
          r["Imp_Pct"] + 1.5,
          i,
          f"{r['Imp_Pct']:.0f}%",
          va="center",
          fontsize=8,
          color=GRIS_OSCURO,
      )

    ax15.set_title(
        "Luxury, Minivans & SUVs rely heavily on imports",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax15.set_xlim(0, 115)
    ax15.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax15)
    st.pyplot(fig15)

  # --- CHART 16: Top Modelos Nacionales vs Top Importados ---
  with c4:
    st.subheader("4.4 Top Domestic vs. Top Imported Models")
    origen_pick = st.radio(
        "View top models by origin:",
        ["NACIONAL", "IMPORTADO"],
        horizontal=True,
    )
    sub_o = df_f[df_f["ORIGEN"] == origen_pick]
    top_o = (
        sub_o.groupby(["MARCA_LIMPIA", "MODELO"], as_index=False)["UNI_VEH"]
        .sum()
        .sort_values("UNI_VEH", ascending=False)
        .head(7)
        .reset_index(drop=True)
    )
    top_o["Label"] = top_o["MARCA_LIMPIA"] + " · " + top_o["MODELO"]

    col_to = ([AZUL] + [AZUL_CLARO] * 2 + [GRIS_CLARO] * 4)[: len(top_o)]
    fig16, ax16 = plt.subplots(figsize=(6.2, 3.3))
    sns.barplot(
        data=top_o,
        x="UNI_VEH",
        y="Label",
        hue="Label",
        palette=dict(zip(top_o["Label"], col_to)),
        legend=False,
        ax=ax16,
    )

    for i, r in top_o.iterrows():
      ax16.text(
          r["UNI_VEH"] + (top_o["UNI_VEH"].max() * 0.02),
          i,
          f"{r['UNI_VEH']/1000:,.0f}k",
          va="center",
          fontsize=8,
          color=GRIS_OSCURO,
      )

    ax16.set_title(
        f"Best-selling {origen_pick.title()} models ({anios[0]}–{anios[1]})",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        color=AZUL,
    )
    ax16.set_xlim(0, top_o["UNI_VEH"].max() * 1.25 if len(top_o) else 100)
    ax16.set(xlabel="", ylabel="", xticks=[])
    estilo_limpio(ax16)
    st.pyplot(fig16)

# ---------------------------------------------------------
# 5. NOTA DE HONESTIDAD METODOLÓGICA EN TODAS LAS PÁGINAS
# ---------------------------------------------------------
st.divider()
st.info("""
**Methodological & Coverage Notes (INEGI RAIAVL):**
* **No Pricing Data:** RAIAVL tracks physical retail unit volume (`UNI_VEH`), not retail prices or revenue. Vehicle segments (*De Lujo*, *Minivans*, *SUV's*, *Compactos*) serve as a structural proxy for product tiering.
* **Non-Reporting Brands & Panel Changes:** Not all automakers report to INEGI—most notably **BYD** is absent from the registry. Additionally, brand entries and exits (such as **GAC** entering with data from January 2024 and **MOTORNATION** exiting from November 2026) shift aggregate totals.
* **Brand Harmonization:** Corporate groups were standardized across 2016–2026 (e.g., consolidating Chrysler, Fiat, Peugeot, and Alfa Romeo under **Stellantis**).
""")


