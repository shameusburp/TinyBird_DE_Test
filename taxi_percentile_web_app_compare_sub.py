# app.py
# Streamlit app WITHOUT DuckDB
# Uses Polars + pyarrow for parquet reading and dataframe-based analytics

import os
import re
import tempfile
from typing import Tuple

import polars as pl

# ==========================
# CONFIG
# ==========================
MILES_TO_KM = 1.60934

# NOTE:
# Streamlit upload size must be set via:
#   streamlit run app.py --server.maxUploadSize=1024
# or ~/.streamlit/config.toml

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ModuleNotFoundError:
    STREAMLIT_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ModuleNotFoundError:
    MATPLOTLIB_AVAILABLE = False


# ==========================
# HELPERS
# ==========================
def extract_month(filename: str) -> str:
    base = os.path.basename(filename)
    match = re.search(r"(\d{4}-\d{2})", base)
    return match.group(1) if match else base.replace(".parquet", "")


def save_uploaded_file(uploaded_file) -> str:
    suffix = ".parquet"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def read_parquet_file(file_path: str) -> pl.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        return pl.read_parquet(file_path)
    except ImportError as exc:
        raise ImportError(
            "Parquet support requires Polars parquet support. "
            "Install with: pip install polars pyarrow"
        ) from exc


# ==========================
# CORE LOGIC
# ==========================
def compute_percentile(df: pl.DataFrame, percentile: float, passenger_filter: str) -> Tuple[float, pl.DataFrame, pl.DataFrame]:
    if not 0.0 <= percentile <= 1.0:
        raise ValueError("Percentile must be between 0.0 and 1.0")

    if "trip_distance" not in df.columns:
        raise ValueError("Missing required column: trip_distance")

    filtered = df.filter(
        pl.col("trip_distance").is_not_null() & (pl.col("trip_distance") > 0)
    )

    if passenger_filter in {"With passengers", "Without passengers"}:
        if "passenger_count" not in filtered.columns:
            raise ValueError("Missing required column for passenger filtering: passenger_count")

        if passenger_filter == "With passengers":
            filtered = filtered.filter(pl.col("passenger_count") > 0)
        else:
            filtered = filtered.filter(pl.col("passenger_count") == 0)

    if filtered.height == 0:
        raise ValueError("No valid rows remain after applying filters")

    threshold = float(
        filtered.select(pl.col("trip_distance").quantile(percentile, interpolation="linear")).item()
    )
    above_threshold = filtered.filter(pl.col("trip_distance") > threshold)

    return threshold, filtered, above_threshold


def build_summary(label: str, filtered_df: pl.DataFrame, above_df: pl.DataFrame, threshold: float) -> dict:
    return {
        "label": label,
        "threshold_miles": threshold,
        "trip_count_filtered": int(filtered_df.height),
        "trip_count_above": int(above_df.height),
        "avg_distance_miles": float(filtered_df.select(pl.col("trip_distance").mean()).item()),
        "total_distance_miles": float(filtered_df.select(pl.col("trip_distance").sum()).item()),
        "above_df": above_df,
        "filtered_df": filtered_df,
    }


# ==========================
# UI RENDERING
# ==========================
def render_file_block(summary: dict, unit: str, title: str) -> Tuple[str, int, float]:
    label = summary["label"]
    threshold_miles = summary["threshold_miles"]
    trip_count = summary["trip_count_filtered"]
    avg_distance_miles = summary["avg_distance_miles"]
    above_df = summary["above_df"]

    if unit == "Kilometers":
        threshold_display = threshold_miles * MILES_TO_KM
        avg_display = avg_distance_miles * MILES_TO_KM
        if "trip_distance" in above_df.columns:
            above_df = above_df.with_columns(
                (pl.col("trip_distance") * MILES_TO_KM).alias("trip_distance")
            )
        unit_label = "km"
    else:
        threshold_display = threshold_miles
        avg_display = avg_distance_miles
        unit_label = "miles"

    st.subheader(f"📊 {title} ({label})")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Threshold", f"{threshold_display:.2f} {unit_label}")
    c2.metric("Trips (filtered)", trip_count)
    c3.metric("Trips above threshold", summary["trip_count_above"])
    c4.metric("Avg distance", f"{avg_display:.2f} {unit_label}")

    cols_to_show = ["trip_distance"]
    for optional_col in ["passenger_count", "pickup_datetime", "tpep_pickup_datetime", "PULocationID", "DOLocationID"]:
        if optional_col in above_df.columns:
            cols_to_show.append(optional_col)

    st.dataframe(above_df.select(cols_to_show).head(200).to_pandas(), use_container_width=True)

    return label, trip_count, avg_display


def render_comparison(results, unit: str):
    labels = [r[0] for r in results]
    counts = [r[1] for r in results]
    avg_distances = [r[2] for r in results]
    unit_label = "km" if unit == "Kilometers" else "miles"

    st.subheader("📈 Month Comparison")

    col1, col2 = st.columns(2)
    col1.metric("Trip count difference", abs(counts[0] - counts[1]))
    col2.metric("Avg distance difference", f"{abs(avg_distances[0] - avg_distances[1]):.2f} {unit_label}")

    if MATPLOTLIB_AVAILABLE:
        fig1, ax1 = plt.subplots()
        ax1.bar(labels, counts)
        ax1.set_title("Number of Trips Between Months")
        ax1.set_ylabel("Trips")
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        ax2.bar(labels, avg_distances)
        ax2.set_title(f"Average Distance Between Months ({unit_label})")
        ax2.set_ylabel(unit_label)
        st.pyplot(fig2)
    else:
        st.info("Install matplotlib to see comparison plots: pip install matplotlib")


# ==========================
# STREAMLIT APP
# ==========================
if STREAMLIT_AVAILABLE:
    st.set_page_config(page_title="Taxi Percentile Comparator", layout="wide")
    st.title("🚕 Taxi Distance Percentile Comparator")
    st.write("Upload up to two parquet files, choose a percentile, and compare trips and distances between months.")

    if "summary1" not in st.session_state:
        st.session_state.summary1 = None
        st.session_state.summary2 = None

    with st.form("input_form"):
        file1 = st.file_uploader("Upload First Month Parquet", type=["parquet"], key="f1")
        file2 = st.file_uploader("Upload Second Month Parquet", type=["parquet"], key="f2")
        percentile = st.number_input("Percentile", min_value=0.0, max_value=1.0, value=0.9, step=0.01)
        passenger_filter = st.selectbox("Passenger Filter", ["All", "With passengers", "Without passengers"])
        submit = st.form_submit_button("Run Analysis")

    unit = st.radio("Display Unit", ["Miles", "Kilometers"], horizontal=True)

    if submit:
        try:
            if not file1 and not file2:
                st.warning("Please upload at least one parquet file.")
            else:
                if file1:
                    path1 = save_uploaded_file(file1)
                    df1 = read_parquet_file(path1)
                    threshold1, filtered1, above1 = compute_percentile(df1, percentile, passenger_filter)
                    st.session_state.summary1 = build_summary(extract_month(file1.name), filtered1, above1, threshold1)
                    os.unlink(path1)
                else:
                    st.session_state.summary1 = None

                if file2:
                    path2 = save_uploaded_file(file2)
                    df2 = read_parquet_file(path2)
                    threshold2, filtered2, above2 = compute_percentile(df2, percentile, passenger_filter)
                    st.session_state.summary2 = build_summary(extract_month(file2.name), filtered2, above2, threshold2)
                    os.unlink(path2)
                else:
                    st.session_state.summary2 = None

                st.success("Analysis complete")
        except Exception as e:
            st.error(f"Error: {e}")

    results = []

    if st.session_state.summary1 is not None:
        results.append(render_file_block(st.session_state.summary1, unit, "File 1"))

    if st.session_state.summary2 is not None:
        results.append(render_file_block(st.session_state.summary2, unit, "File 2"))

    if len(results) == 2:
        render_comparison(results, unit)


# ==========================
# TESTS
# ==========================
def _run_tests():
    df1 = pl.DataFrame({
        "trip_distance": [1.0, 2.0, 3.0, 4.0, 5.0],
        "passenger_count": [0, 1, 1, 0, 2],
    })
    df2 = pl.DataFrame({
        "trip_distance": [2.0, 4.0, 6.0, 8.0, 10.0],
        "passenger_count": [0, 2, 2, 0, 4],
    })

    t1, filtered1, above1 = compute_percentile(df1, 0.9, "All")
    t2, filtered2, above2 = compute_percentile(df2, 0.9, "All")

    assert t2 > t1, "Comparison logic failed"
    assert filtered1.height == 5, "Unexpected filtered row count"
    assert above1.height >= 1, "Expected at least one trip above threshold"

    _, filtered_with, _ = compute_percentile(df1, 0.5, "With passengers")
    assert filtered_with.select((pl.col("passenger_count") > 0).all()).item(), "With-passengers filter failed"

    _, filtered_without, _ = compute_percentile(df1, 0.5, "Without passengers")
    assert filtered_without.select((pl.col("passenger_count") == 0).all()).item(), "Without-passengers filter failed"

    try:
        compute_percentile(pl.DataFrame({"distance": [1, 2, 3]}), 0.9, "All")
        assert False, "Expected missing trip_distance to fail"
    except ValueError:
        pass

    try:
        compute_percentile(pl.DataFrame({"trip_distance": [0, 0, -1]}), 0.9, "All")
        assert False, "Expected empty filtered dataset to fail"
    except ValueError:
        pass

    # Additional test: missing passenger_count when a passenger filter is requested
    try:
        compute_percentile(pl.DataFrame({"trip_distance": [1.0, 2.0, 3.0]}), 0.5, "With passengers")
        assert False, "Expected missing passenger_count to fail"
    except ValueError:
        pass

    print("All tests passed")


if __name__ == "__main__" and not STREAMLIT_AVAILABLE:
    _run_tests()
