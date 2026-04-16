# TinyBird_DE_Test
TinyBird Data Engineer Test

Author: James Powenski

This python application is a local web application that uses parquet files from the NY Taxi service, https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

My approach was initially to find the 90 precentile of the distance traveled for a specific month but I went a little farther by curiousity to see how Uber influenced the data therefore the application can compare one month to another month. Uber started in May 2011. The 2009 data doesn't seem to have distance data therefore use months from Jan 2010 forward.

The default distance from NY Taxi is in miles.

I used ChatGPT which suggested to use 'streamlit' for the UI and python for the application. The requirement was to use libraries only and not a 3rd party solution like DuckDB which is a parquet file database with SQL.

# 🚕 Taxi Distance Percentile Comparator

![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Polars](https://img.shields.io/badge/Polars-DataFrame-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A lightweight analytics web app for exploring NYC taxi trip data and comparing distance patterns between months.

Built with:

* ⚡ **Streamlit** (UI)
* 🧠 **Polars** (fast dataframe engine)
* 📦 **PyArrow** (parquet support)
* 📊 **Matplotlib** (visualizations)

---

## ✨ Features

* Upload **one or two parquet files**
* Compute **percentiles (e.g., P90)** on trip distance
* Filter by:

  * All trips
  * With passengers
  * Without passengers
* Toggle units:

  * Miles ↔ Kilometers
* Compare two months:

  * Trip counts
  * Average distance
  * Differences
* Visualizations:

  * Bar charts for comparison

---

## 📸 Screenshots (add your own)

> Add screenshots here after running the app

* Upload UI
* Results dashboard
* Comparison charts

---

## 📂 Expected Data Schema

Required:

* `trip_distance`

Optional (used for filtering/display):

* `passenger_count`
* `pickup_datetime`
* `tpep_pickup_datetime`
* `PULocationID`
* `DOLocationID`

---

## 🧠 How It Works

For each file:

1. Load parquet → Polars DataFrame
2. Clean data:

   * remove nulls
   * remove zero/negative distances
3. Apply passenger filter
4. Compute percentile:

   ```python
   df.select(pl.col("trip_distance").quantile(p))
   ```
5. Filter trips above threshold
6. Display summary + results

---

## ⚙️ Installation

```bash
pip install streamlit polars pyarrow matplotlib pandas
```

---

## ▶️ Run the App

### Basic

```bash
streamlit run app.py
```

### With 1GB Upload Limit

```bash
streamlit run app.py --server.maxUploadSize=1024
```

---

## ⚙️ Config (Optional)

Create:

```bash
~/.streamlit/config.toml
```

```toml
[server]
maxUploadSize = 1024
```

---

## 🧪 Usage

### Single File Analysis

1. Upload file
2. Select percentile (e.g. 0.9)
3. Choose filter
4. Click **Run Analysis**

### Two File Comparison

1. Upload both months
2. Click **Run Analysis**
3. View:

   * side-by-side metrics
   * comparison charts

---

## 📊 Example Use Cases

* Compare January vs February trip distances
* Detect long-trip outliers
* Analyze passenger vs non-passenger behavior
* Track changes in trip patterns over time

---

## ⚠️ Common Issues

### Upload limit error

❌ Don't do this in code:

```python
st.set_option('server.maxUploadSize', ...)
```

✅ Do this instead:

```bash
streamlit run app.py --server.maxUploadSize=1024
```

---

### Missing parquet support

```bash
pip install pyarrow
```

---

### Missing columns

* Must have: `trip_distance`
* For filters: `passenger_count`

---

### Empty results

Caused by:

* filtering removes all rows
* bad data (0 or negative distances)

---

## ⚡ Performance Notes

* Polars is fast and memory-efficient
* Large parquet files still depend on RAM
* For very large datasets:

  * consider local file access instead of upload
  * or cloud storage (S3/GCS)

---

## 🧪 Tests

Includes tests for:

* percentile correctness
* filtering logic
* comparison behavior
* error handling

Run automatically outside Streamlit mode.

---

## 🚀 Future Improvements

* 📥 Download results (CSV/Parquet)
* 📊 Multi-month trend analysis
* 📈 Time-series visualizations
* ☁️ Cloud storage integration
* ⚡ Streaming large datasets

---

## 🏁 Summary

A fast, interactive tool for exploring taxi trip distance distributions and comparing behavior across months using a clean UI and efficient backend.
