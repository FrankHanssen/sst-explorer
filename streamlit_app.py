import calendar
import datetime
import math

from pathlib import Path

import ee
import folium
import numpy as np
import pandas as pd
import statsmodels.api as sm
import streamlit as st

from folium.plugins import Draw
from scipy import stats
from streamlit_folium import st_folium


# ==========================================================
# PAGE
# ==========================================================

st.set_page_config(
    page_title="Sea suface temperature change explorer",
    page_icon="🌊",
    layout="wide",
)


# ==========================================================
# GLOBAL READABILITY
# ==========================================================

st.markdown(
    """
    <style>

    .stApp {
        font-size: 23px !important;
    }

    /* ------------------------------------------------------
       SECTION HEADINGS
       ------------------------------------------------------ */

    h2 {
        font-size: 36px !important;
        line-height: 1.20 !important;
        font-weight: 700 !important;
    }

    h3 {
        font-size: 30px !important;
        line-height: 1.25 !important;
        font-weight: 650 !important;
    }

    /* ------------------------------------------------------
       BODY TEXT
       ------------------------------------------------------ */

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span {
        font-size: 23px !important;
        line-height: 1.62 !important;
    }

    /* ------------------------------------------------------
       CAPTIONS / SMALL TEXT
       ------------------------------------------------------ */

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stCaptionContainer"] span,
    small {
        font-size: 20px !important;
        line-height: 1.55 !important;
    }

    /* ------------------------------------------------------
       SIDEBAR
       ------------------------------------------------------ */

    [data-testid="stSidebar"] {
        font-size: 21px !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        font-size: 21px !important;
        line-height: 1.50 !important;
    }

    [data-testid="stSidebar"] h2 {
        font-size: 30px !important;
    }

    [data-testid="stSidebar"] h3 {
        font-size: 26px !important;
    }

    /* ------------------------------------------------------
       WIDGETS
       ------------------------------------------------------ */

    [data-testid="stRadio"] label,
    [data-testid="stRadio"] p,
    [data-testid="stRadio"] span,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        font-size: 21px !important;
    }

    [data-baseweb="select"],
    [data-baseweb="select"] *,
    [data-baseweb="popover"],
    [data-baseweb="popover"] * {
        font-size: 21px !important;
    }

    [data-testid="stSlider"] p,
    [data-testid="stSlider"] span {
        font-size: 21px !important;
    }

    /* ------------------------------------------------------
       ALERTS
       ------------------------------------------------------ */

    [data-testid="stAlert"],
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div {
        font-size: 22px !important;
        line-height: 1.58 !important;
    }

    /* ------------------------------------------------------
       METRICS
       ------------------------------------------------------ */

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span,
    [data-testid="stMetricLabel"] div {
        font-size: 20px !important;
        line-height: 1.4 !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        font-size: 36px !important;
        line-height: 1.2 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 20px !important;
    }

    /* ------------------------------------------------------
       EXPANDERS
       ------------------------------------------------------ */

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        font-size: 22px !important;
        font-weight: 650 !important;
    }

    [data-testid="stExpander"] p,
    [data-testid="stExpander"] li,
    [data-testid="stExpander"] span {
        font-size: 21px !important;
        line-height: 1.62 !important;
    }

    /* ------------------------------------------------------
       BUTTONS
       ------------------------------------------------------ */

    .stButton button,
    .stButton button p,
    .stDownloadButton button,
    .stDownloadButton button p {
        font-size: 21px !important;
        line-height: 1.4 !important;
    }

    /* ------------------------------------------------------
       SPINNER
       ------------------------------------------------------ */

    [data-testid="stSpinner"],
    [data-testid="stSpinner"] p,
    [data-testid="stSpinner"] span {
        font-size: 21px !important;
    }

    /* ------------------------------------------------------
       CUSTOM MAIN TITLE
       ------------------------------------------------------ */

    .sst-main-title {
        font-size: 75px !important;
        font-weight: 700 !important;
        line-height: 1.0;
        white-space: nowrap;
        position: relative;
        top: 26px;
    }

    @media (max-width: 900px) {
        .sst-main-title {
            font-size: 52px !important;
        }
    }

    @media (max-width: 600px) {
        .sst-main-title {
            font-size: 42px !important;
        }
    }

    /* ------------------------------------------------------
       AUTHOR
       ------------------------------------------------------ */

    .developer-line {
        font-size: 20px !important;
        line-height: 1.5 !important;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #555;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HEADER: NINA LOGO + MAIN TITLE
# ==========================================================

from pathlib import Path

logo_path = Path(__file__).parent / "assets" / "nina_logo.png"

logo_col, title_col = st.columns(
    [0.9, 7],
    gap="small",
    vertical_alignment="center"
)

with logo_col:
    st.image(str(logo_path), width=290)

with title_col:
    st.markdown(
        """
        <div class="sst-main-title">
            🌊 Sea surface temperature change explorer
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================================
# INTRODUCTION
# ==========================================================

st.write(
    """
Explore long-term sea-surface-temperature change using NOAA OISST
and Google Earth Engine.

Choose **Point** to click on an ocean location, or **Polygon** to
draw a study region. The app calculates the historical SST anomaly
time series and estimates the long-term trend.
"""
)


# ==========================================================
# SST ANOMALY EXPLANATION
# ==========================================================

with st.expander(
    "🌡️ What is an SST anomaly?",
    expanded=False,
):

    st.markdown(
        """
**SST** stands for **sea surface temperature**. An **SST anomaly** shows how much warmer or colder the ocean surface is than the long-term average for the same place and time of year.  
For example, **+1.0 °C** means 1.0 °C warmer than average and **−1.0 °C** means 1.0 °C colder; it shows the **difference from typical conditions**, not the actual temperature.
"""
    )


# ==========================================================
# EARTH ENGINE
# ==========================================================

ee.Initialize(
    project="p-312432-birdwake"
)

OISST = ee.ImageCollection(
    "NOAA/CDR/OISST/V2_1"
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "map_lat" not in st.session_state:
    st.session_state.map_lat = 65.0

if "map_lon" not in st.session_state:
    st.session_state.map_lon = 5.0

if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 4

if "selected_point" not in st.session_state:
    st.session_state.selected_point = None

if "selected_polygon" not in st.session_state:
    st.session_state.selected_polygon = None


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header(
    "Analysis settings"
)

analysis_mode = st.sidebar.radio(
    "Analysis mode",
    [
        "Point",
        "Polygon",
    ],
)

year = st.sidebar.slider(
    "Map year",
    min_value=1982,
    max_value=2026,
    value=2026,
)


# ----------------------------------------------------------
# 2026 is currently available through June
# ----------------------------------------------------------

if year == 2026:

    available_months = list(
        range(1, 7)
    )

    default_month_index = 5

else:

    available_months = list(
        range(1, 13)
    )

    default_month_index = 6


month = st.sidebar.selectbox(
    "Month",
    options=available_months,
    index=default_month_index,
    format_func=lambda m: calendar.month_name[m],
)


# ----------------------------------------------------------
# Historical analysis period
#
# January–June: include 2026
# July–December: latest complete observation is 2025
# ----------------------------------------------------------

if month <= 6:
    analysis_end_year = 2026
else:
    analysis_end_year = 2025


if st.sidebar.button(
    "Clear selection"
):

    if analysis_mode == "Point":
        st.session_state.selected_point = None
    else:
        st.session_state.selected_polygon = None

    st.rerun()


# ==========================================================
# CURRENT MONTH
# ==========================================================

start_date = datetime.date(
    year,
    month,
    1,
)

if month == 12:

    end_date = datetime.date(
        year + 1,
        1,
        1,
    )

else:

    end_date = datetime.date(
        year,
        month + 1,
        1,
    )


sst_anomaly = (
    OISST
    .filterDate(
        str(start_date),
        str(end_date),
    )
    .select("anom")
    .mean()
    .multiply(0.01)
)


# ==========================================================
# VISUALIZATION
# ==========================================================

palette = [
    "#313695",
    "#4575b4",
    "#74add1",
    "#abd9e9",
    "#e0f3f8",
    "#ffffbf",
    "#fee090",
    "#fdae61",
    "#f46d43",
    "#d73027",
    "#a50026",
]

vis_params = {
    "min": -3,
    "max": 3,
    "palette": [
        color.replace("#", "")
        for color in palette
    ],
}

map_id = sst_anomaly.getMapId(
    vis_params
)

tile_url = (
    map_id["tile_fetcher"]
    .url_format
)


# ==========================================================
# MAP
# ==========================================================

m = folium.Map(
    location=[
        st.session_state.map_lat,
        st.session_state.map_lon,
    ],
    zoom_start=st.session_state.map_zoom,
    tiles="CartoDB positron",
    control_scale=True,
)


# ==========================================================
# FOLIUM / LEAFLET READABILITY
# ==========================================================

map_css = """
<style>

/* Layer control */
.leaflet-control-layers {
    font-size: 18px !important;
    line-height: 1.4 !important;
}

.leaflet-control-layers label,
.leaflet-control-layers span {
    font-size: 18px !important;
}

/* Map scale */
.leaflet-control-scale-line {
    font-size: 15px !important;
}

/* Attribution */
.leaflet-control-attribution,
.leaflet-control-attribution a {
    font-size: 13px !important;
}

/* Tooltips */
.leaflet-tooltip,
.leaflet-popup-content {
    font-size: 18px !important;
    line-height: 1.45 !important;
}

/* Drawing tools */
.leaflet-draw-tooltip,
.leaflet-draw-tooltip-single,
.leaflet-draw-actions a {
    font-size: 17px !important;
}

/* Zoom controls */
.leaflet-control-zoom a {
    font-size: 24px !important;
}

</style>
"""

m.get_root().html.add_child(
    folium.Element(
        map_css
    )
)


# ==========================================================
# EARTH ENGINE MAP LAYER
# ==========================================================

folium.TileLayer(
    tiles=tile_url,
    attr="Google Earth Engine / NOAA OISST",
    name=(
        f"SST anomaly "
        f"{calendar.month_name[month]} {year}"
    ),
    overlay=True,
    control=True,
).add_to(m)


# ==========================================================
# PERSIST PREVIOUS POINT
# ==========================================================

if (
    analysis_mode == "Point"
    and st.session_state.selected_point
):

    p = st.session_state.selected_point

    folium.CircleMarker(
        location=[
            p["lat"],
            p["lng"],
        ],
        radius=7,
        weight=3,
        fill=True,
        fill_opacity=0.8,
        tooltip="Selected point",
    ).add_to(m)


# ==========================================================
# PERSIST PREVIOUS POLYGON
# ==========================================================

if (
    analysis_mode == "Polygon"
    and st.session_state.selected_polygon
):

    folium.GeoJson(
        st.session_state.selected_polygon,
        name="Selected region",
        style_function=lambda feature: {
            "weight": 3,
            "fillOpacity": 0.10,
        },
    ).add_to(m)


# ==========================================================
# POLYGON DRAWING TOOLS
# ==========================================================

if analysis_mode == "Polygon":

    Draw(
        export=False,
        position="topleft",
        draw_options={
            "polyline": False,
            "rectangle": True,
            "circle": False,
            "circlemarker": False,
            "marker": False,
            "polygon": True,
        },
        edit_options={
            "edit": True,
            "remove": True,
        },
    ).add_to(m)


# ==========================================================
# CUSTOM SST COLOR BAR — LOWER RIGHT
# ==========================================================

legend_html = """
<div style="
    position: fixed;
    bottom: 42px;
    right: 24px;
    z-index: 9999;

    width: 370px;

    padding: 12px 14px 11px 14px;

    background: rgba(255, 255, 255, 0.96);

    border: 1px solid rgba(0, 0, 0, 0.22);
    border-radius: 7px;

    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.24);

    font-family: Arial, Helvetica, sans-serif;
">

    <div style="
        font-size: 18px;
        font-weight: 700;
        line-height: 1.2;
        color: #222;
        margin-bottom: 8px;
    ">
        SST anomaly (°C)
    </div>

    <div style="
        width: 100%;
        height: 20px;

        border: 1px solid rgba(0, 0, 0, 0.28);
        border-radius: 2px;

        background: linear-gradient(
            to right,
            #313695 0%,
            #4575b4 10%,
            #74add1 20%,
            #abd9e9 30%,
            #e0f3f8 40%,
            #ffffbf 50%,
            #fee090 60%,
            #fdae61 70%,
            #f46d43 80%,
            #d73027 90%,
            #a50026 100%
        );
    ">
    </div>

    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;

        width: 100%;
        margin-top: 6px;

        font-size: 16px;
        font-weight: 600;
        line-height: 1;

        color: #222;
    ">
        <span>−3</span>
        <span>−2</span>
        <span>−1</span>
        <span>0</span>
        <span>+1</span>
        <span>+2</span>
        <span>+3</span>
    </div>

    <div style="
        display: flex;
        justify-content: space-between;

        margin-top: 7px;

        font-size: 13px;
        font-weight: 500;
        color: #555;
    ">
        <span>Colder than average</span>
        <span>Warmer than average</span>
    </div>

</div>
"""

m.get_root().html.add_child(
    folium.Element(
        legend_html
    )
)


# ==========================================================
# LAYER CONTROL
# ==========================================================

folium.LayerControl().add_to(m)


# ==========================================================
# MAP HEADING
# ==========================================================

st.subheader(
    f"SST anomaly — "
    f"{calendar.month_name[month]} {year}"
)

st.write(
    "Blue areas are colder than the long-term average, "
    "while red areas are warmer than the long-term average. "
    "The color scale shows the SST anomaly in °C."
)


# ==========================================================
# DISPLAY MAP
# ==========================================================

map_data = st_folium(
    m,
    width=None,
    height=650,
    key="sst_map",
)


# ==========================================================
# REMEMBER MAP VIEW
# ==========================================================

if map_data:

    center = map_data.get(
        "center"
    )

    if center:

        st.session_state.map_lat = (
            center["lat"]
        )

        st.session_state.map_lon = (
            center["lng"]
        )

    zoom = map_data.get(
        "zoom"
    )

    if zoom is not None:

        st.session_state.map_zoom = (
            zoom
        )


# ==========================================================
# CAPTURE SELECTION
# ==========================================================

if analysis_mode == "Point":

    clicked = map_data.get(
        "last_clicked"
    )

    if clicked:

        st.session_state.selected_point = {
            "lat": clicked["lat"],
            "lng": clicked["lng"],
        }


else:

    drawings = map_data.get(
        "all_drawings"
    )

    if drawings:

        latest = drawings[-1]

        if "geometry" in latest:

            st.session_state.selected_polygon = (
                latest["geometry"]
            )


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def monthly_image_for_year(y):

    start = ee.Date.fromYMD(
        y,
        month,
        1,
    )

    end = start.advance(
        1,
        "month",
    )

    return (
        OISST
        .filterDate(
            start,
            end,
        )
        .select("anom")
        .mean()
        .multiply(0.01)
    )


def point_value(
    image,
    geometry,
):

    return image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=25000,
        maxPixels=1e8,
    ).get("anom")


def area_weighted_value(
    image,
    geometry,
):

    pixel_area = (
        ee.Image.pixelArea()
    )

    valid_area = (
        pixel_area
        .updateMask(
            image.mask()
        )
    )

    weighted = (
        image
        .multiply(
            pixel_area
        )
    )

    numerator = (
        weighted
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=25000,
            maxPixels=1e9,
            bestEffort=True,
        )
        .get("anom")
    )

    denominator = (
        valid_area
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=25000,
            maxPixels=1e9,
            bestEffort=True,
        )
        .get("area")
    )

    return ee.Algorithms.If(
        ee.Algorithms.IsEqual(
            numerator,
            None,
        ),
        None,
        ee.Number(
            numerator
        ).divide(
            ee.Number(
                denominator
            )
        ),
    )


# ==========================================================
# BUILD HISTORICAL TIME SERIES
# ==========================================================

def build_time_series(
    geometry,
    polygon_mode,
):

    years = ee.List.sequence(
        1982,
        analysis_end_year,
    )

    def make_feature(y):

        y = (
            ee.Number(y)
            .toInt()
        )

        image = (
            monthly_image_for_year(
                y
            )
        )

        if polygon_mode:

            value = (
                area_weighted_value(
                    image,
                    geometry,
                )
            )

        else:

            value = (
                point_value(
                    image,
                    geometry,
                )
            )

        return ee.Feature(
            None,
            {
                "year": y,
                "anomaly": value,
            },
        )

    fc = ee.FeatureCollection(
        years.map(
            make_feature
        )
    )

    data = fc.getInfo()

    rows = []

    for feature in data[
        "features"
    ]:

        props = feature[
            "properties"
        ]

        if props[
            "anomaly"
        ] is not None:

            rows.append(
                {
                    "Year":
                        props["year"],

                    "SST anomaly":
                        props["anomaly"],
                }
            )

    return pd.DataFrame(
        rows
    )


# ==========================================================
# TREND ANALYSIS
# ==========================================================

def analyse_trend(df):

    x = (
        df["Year"]
        .to_numpy(
            dtype=float
        )
    )

    y = (
        df["SST anomaly"]
        .to_numpy(
            dtype=float
        )
    )

    X = sm.add_constant(
        x
    )

    ols = sm.OLS(
        y,
        X,
    ).fit()

    n = len(df)

    hac_lags = max(
        1,
        int(
            math.floor(
                4
                * (n / 100)
                ** (2 / 9)
            )
        ),
    )

    hac = (
        ols
        .get_robustcov_results(
            cov_type="HAC",
            maxlags=hac_lags,
        )
    )

    slope = (
        hac.params[1]
    )

    p_value = (
        hac.pvalues[1]
    )

    ci = (
        hac
        .conf_int(
            alpha=0.05
        )[1]
    )

    trend_decade = (
        slope * 10
    )

    ci_low = (
        ci[0] * 10
    )

    ci_high = (
        ci[1] * 10
    )

    residuals = (
        ols.resid
    )

    if len(
        residuals
    ) > 2:

        lag1_r = (
            np.corrcoef(
                residuals[:-1],
                residuals[1:],
            )[0, 1]
        )

    else:

        lag1_r = np.nan

    kendall = (
        stats.kendalltau(
            x,
            y,
            nan_policy="omit",
        )
    )

    sen = (
        stats.theilslopes(
            y,
            x,
            alpha=0.95,
        )
    )

    result = {
        "trend_decade":
            trend_decade,

        "ci_low":
            ci_low,

        "ci_high":
            ci_high,

        "p_value":
            p_value,

        "lag1_r":
            lag1_r,

        "kendall_tau":
            kendall.statistic,

        "kendall_p":
            kendall.pvalue,

        "sen_decade":
            sen.slope * 10,

        "sen_low":
            sen.low_slope * 10,

        "sen_high":
            sen.high_slope * 10,

        "hac_lags":
            hac_lags,
    }

    df[
        "Linear trend"
    ] = (
        ols.params[0]
        + ols.params[1]
        * x
    )

    return (
        result,
        df,
    )


# ==========================================================
# PLAIN-LANGUAGE INTERPRETATION
# ==========================================================

def plain_language_interpretation(
    result,
):

    trend = result[
        "trend_decade"
    ]

    low = result[
        "ci_low"
    ]

    high = result[
        "ci_high"
    ]

    p = result[
        "p_value"
    ]

    sen = result[
        "sen_decade"
    ]

    kendall_p = result[
        "kendall_p"
    ]

    if trend > 0:
        direction = "warming"
    else:
        direction = "cooling"

    magnitude = abs(
        trend
    )

    if magnitude < 0.1:
        strength = "a small"

    elif magnitude < 0.3:
        strength = "a moderate"

    else:
        strength = "a relatively strong"

    if p < 0.05:

        evidence = (
            "The statistical evidence that this "
            f"{direction} trend is real is reasonably strong: "
            "the 95% uncertainty interval does not include zero."
        )

    else:

        evidence = (
            "The estimated trend is uncertain. "
            "The 95% uncertainty interval includes zero, "
            "so the available record does not clearly distinguish "
            "the trend from natural year-to-year variation."
        )

    robust_agreement = (
        np.sign(
            trend
        )
        ==
        np.sign(
            sen
        )
    )

    if (
        robust_agreement
        and kendall_p < 0.05
        and p < 0.05
    ):

        agreement = (
            "Two additional robust statistical checks agree "
            "with the main analysis, which increases confidence "
            "in the direction of change."
        )

    elif (
        p < 0.05
        or kendall_p < 0.05
    ):

        agreement = (
            "The different statistical methods do not agree "
            "completely, so the result should be interpreted "
            "with some caution."
        )

    else:

        agreement = (
            "None of the statistical methods provides strong "
            "evidence for a persistent long-term trend."
        )

    return (
        f"For the selected location or region, "
        f"{calendar.month_name[month]} sea-surface temperature "
        f"shows {strength} {direction} tendency of about "
        f"**{magnitude:.2f} °C per decade** since 1982. "
        f"The estimated 95% range is "
        f"**{low:+.2f} to {high:+.2f} °C per decade**. "
        f"{evidence} "
        f"{agreement}"
    )


# ==========================================================
# DETERMINE ACTIVE GEOMETRY
# ==========================================================

geometry = None
polygon_mode = False
selection_label = None
current_value = None
area_km2 = None


# ==========================================================
# POINT MODE
# ==========================================================

if (
    analysis_mode == "Point"
    and st.session_state.selected_point
):

    p = (
        st.session_state
        .selected_point
    )

    geometry = ee.Geometry.Point(
        [
            p["lng"],
            p["lat"],
        ]
    )

    selection_label = (
        f"{p['lat']:.3f}, "
        f"{p['lng']:.3f}"
    )

    current_value = (
        point_value(
            sst_anomaly,
            geometry,
        )
        .getInfo()
    )


# ==========================================================
# POLYGON MODE
# ==========================================================

elif (
    analysis_mode == "Polygon"
    and st.session_state.selected_polygon
):

    polygon_mode = True

    geometry = ee.Geometry(
        st.session_state
        .selected_polygon
    )

    area_km2 = (
        geometry
        .area(
            maxError=1000
        )
        .divide(
            1_000_000
        )
        .getInfo()
    )

    selection_label = (
        f"{area_km2:,.0f} km² region"
    )

    try:

        current_value = (
            ee.Number(
                area_weighted_value(
                    sst_anomaly,
                    geometry,
                )
            )
            .getInfo()
        )

    except Exception:

        current_value = None


# ==========================================================
# ANALYSIS
# ==========================================================

if geometry is not None:

    st.divider()

    st.subheader(
        "Selected area"
    )

    col1, col2 = (
        st.columns(
            2
        )
    )

    with col1:

        if polygon_mode:

            st.metric(
                "Region area",
                f"{area_km2:,.0f} km²",
            )

        else:

            st.metric(
                "Location",
                selection_label,
            )

    with col2:

        if current_value is None:

            st.metric(
                f"{calendar.month_name[month]} {year}",
                "No ocean data",
            )

        else:

            st.metric(
                (
                    "Mean SST anomaly — "
                    f"{calendar.month_name[month]} {year}"
                ),
                f"{current_value:+.2f} °C",
            )


    # ======================================================
    # TIME SERIES
    # ======================================================

    with st.spinner(
        f"Earth Engine is calculating the "
        f"1982–{analysis_end_year} climate record..."
    ):

        df = (
            build_time_series(
                geometry,
                polygon_mode,
            )
        )


    if len(df) >= 5:

        result, df = (
            analyse_trend(
                df
            )
        )


        # ==================================================
        # PLAIN LANGUAGE SUMMARY
        # ==================================================

        st.subheader(
            "What does the result mean?"
        )

        st.markdown(
            plain_language_interpretation(
                result
            )
        )

        st.write(
            f"This is a statistical interpretation of the observed "
            f"1982–{analysis_end_year} record. It does not by itself "
            f"establish the physical cause of the change."
        )


        # ==================================================
        # MAIN METRICS
        # ==================================================

        st.subheader(
            "Climate trend"
        )

        metric1, metric2, metric3 = (
            st.columns(
                3
            )
        )

        with metric1:

            st.metric(
                "Estimated change",
                (
                    f"{result['trend_decade']:+.2f} "
                    "°C / decade"
                ),
            )

        with metric2:

            st.metric(
                "95% uncertainty range",
                (
                    f"{result['ci_low']:+.2f} to "
                    f"{result['ci_high']:+.2f}"
                ),
            )

        with metric3:

            if (
                result["p_value"]
                < 0.05
            ):

                evidence_text = (
                    "Strong evidence"
                )

            else:

                evidence_text = (
                    "Uncertain"
                )

            st.metric(
                "Evidence for trend",
                evidence_text,
            )


        # ==================================================
        # CHART
        # ==================================================

        st.subheader(
            f"{calendar.month_name[month]} "
            "SST anomaly history"
        )

        chart_df = (
            df
            .set_index(
                "Year"
            )[
                [
                    "SST anomaly",
                    "Linear trend",
                ]
            ]
        )

        st.line_chart(
            chart_df
        )

        st.write(
            "The fluctuating line shows individual years. "
            "The straight line shows the fitted long-term trend."
        )


        # ==================================================
        # CSV DOWNLOAD
        # ==================================================

        csv_data = (
            df[
                [
                    "Year",
                    "SST anomaly",
                ]
            ]
            .to_csv(
                index=False
            )
            .encode(
                "utf-8"
            )
        )

        st.download_button(
            label=(
                "⬇️ Download time series as CSV"
            ),
            data=csv_data,
            file_name=(
                f"oisst_"
                f"{calendar.month_name[month].lower()}_"
                f"1982_{analysis_end_year}.csv"
            ),
            mime="text/csv",
        )


        # ==================================================
        # ROBUST CHECKS
        # ==================================================

        with st.expander(
            "Robust statistical checks"
        ):

            col1, col2, col3 = (
                st.columns(
                    3
                )
            )

            with col1:

                st.metric(
                    "Theil–Sen trend",
                    (
                        f"{result['sen_decade']:+.2f} "
                        "°C / decade"
                    ),
                )

            with col2:

                st.metric(
                    "Theil–Sen 95% CI",
                    (
                        f"{result['sen_low']:+.2f} to "
                        f"{result['sen_high']:+.2f}"
                    ),
                )

            with col3:

                st.metric(
                    "Kendall p-value",
                    (
                        f"{result['kendall_p']:.4f}"
                    ),
                )

            st.write(
                "Kendall τ: "
                f"**{result['kendall_tau']:+.3f}**"
            )

            st.write(
                "Lag-1 residual correlation: "
                f"**{result['lag1_r']:+.3f}**"
            )


        # ==================================================
        # EXPLANATION FOR NON-EXPERTS
        # ==================================================

        with st.expander(
            "What do these statistics mean?"
        ):

            st.markdown(
                """
### Trend in °C per decade

This tells you the estimated average rate of change.

For example:

**+0.30 °C per decade**

means that the selected month's sea-surface temperature
has increased by approximately 0.30 °C every ten years
over the period analysed.

---

### 95% uncertainty range

No trend estimate is exact.

The 95% interval describes a plausible range around the
estimated trend.

For example:

**+0.18 to +0.42 °C per decade**

means that the data are consistent with warming somewhere
within approximately that range.

If the interval crosses **zero**, the data do not provide
strong evidence that the long-term trend differs from no
change.

---

### HAC / Newey–West adjustment

Climate observations in neighbouring years can be related
to one another.

A warm year may be more likely to be followed by another
warm year, for example.

The HAC method adjusts the estimated uncertainty so that
this temporal dependence is less likely to make a trend
appear more certain than it really is.

---

### Theil–Sen trend

The Theil–Sen estimator is another way of estimating the
rate of change.

It is less sensitive to unusually warm or cold individual
years than ordinary linear regression.

If the Theil–Sen result is similar to the main trend
estimate, that provides useful reassurance that individual
extreme years are not driving the result.

---

### Kendall trend test

The Kendall test asks a slightly different question:

> Do temperatures tend to increase consistently through time?

It does not require the temperature changes to follow a
perfect straight line.

A small p-value suggests evidence of a persistent monotonic
trend.

---

### Why use several methods?

No statistical method is perfect.

If the HAC-adjusted regression, Theil–Sen estimate and
Kendall test all point in the same direction, confidence in
the overall interpretation is stronger than when relying on
one statistic alone.
"""
            )


        # ==================================================
        # SCIENTIFIC DETAILS
        # ==================================================

        with st.expander(
            "Scientific and methodological details"
        ):

            st.write(
                f"Observations used: "
                f"**{len(df)} annual values**"
            )

            st.write(
                f"Analysis period: "
                f"**1982–{analysis_end_year}**"
            )

            st.write(
                f"HAC lag parameter: "
                f"**{result['hac_lags']}**"
            )

            if polygon_mode:

                st.markdown(
                    """
### Spatial averaging

The polygon analysis uses an **area-weighted mean**.

Each valid OISST pixel is weighted according to its physical
surface area before calculating the regional mean.

This is particularly important at high latitudes because
geographic raster cells do not all represent exactly the
same physical surface area.
"""
                )

            else:

                st.markdown(
                    """
### Point analysis

The point result represents the OISST raster value at the
selected geographic location at approximately the native
scale of the dataset.
"""
                )

            st.markdown(
                """
### Statistical scope

These calculations describe statistical change in the
selected monthly SST anomaly series.

They do not by themselves identify the physical cause of
the observed change and should not be interpreted as a
complete climate-attribution analysis.

The Kendall result is used here as a robust monotonic-trend
cross-check.

The HAC-adjusted regression is the primary
autocorrelation-aware uncertainty estimate used in this app.
"""
            )


    else:

        st.warning(
            "Not enough valid ocean observations were available "
            "for trend analysis."
        )


# ==========================================================
# DATA SOURCE / AUTHOR
# ==========================================================

st.divider()

st.write(
    "**Data source:** NOAA OISST V2.1 via Google Earth Engine.  \n"
    f"**Analysis period:** 1982–{analysis_end_year} "
    f"for {calendar.month_name[month]}."
)

st.markdown(
    """
    <div class="developer-line">
        Developed by <strong>Frank Hanssen</strong>
    </div>
    """,
    unsafe_allow_html=True,
)