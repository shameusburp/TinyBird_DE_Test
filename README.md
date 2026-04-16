# TinyBird_DE_Test
TinyBird Data Engineer Test

Author: James Powenski

This python application is a local web application that uses parquet files from the NY Taxi service, https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Specifically the application uses 'Yellow Taxi Trip Records' parquet files.

The application can find variable distance percentile but the default is set to 90th percentile.

The application can compare two different months of data to compare and create a histogram of the data. I thought it was an interesting experiment to see the data before Uber started on May 2011 vs the present, 10 year difference vs the present and closer year differences.

Also, the data showed trips with or without passengers therefore analysis can be performed with or without passengers or both.

A simple radial button can switch between miles and kilometers. The default metric in the data is miles.

The data is presented as below.

Threshold (90), Number of trips, Number of Trips above the threshold, average distance.

The raw table of the data is presented and can be downloaded as a csv file.

Finally Histograms show the compared files data of number of trips and distance traveled.

How to run the application at the command line assuming python and pip are installed.

pip install streamlit polars pyarrow matplotlib pandas

streamlit run taxi_percentile_web_app_compare_sub.py --server.maxUploadSize=1024

Go to http://localhost:8501/ in a web browser

