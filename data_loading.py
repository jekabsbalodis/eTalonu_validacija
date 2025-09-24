"""
Data loading functions to download and extract .zip file
based on url from month_data.py.
"""

import datetime
import pathlib
import tempfile
import zipfile

import polars as pl
import requests
import streamlit as st

from month_data import available_months


def get_months(
    start_date: datetime.date,
    end_date: datetime.date,
) -> list[tuple[int, int]] | None:
    """
    Get a list of (year, month) tuples between start_date and end_date inclusive.

    Args:
        start_date: Start date.
        end_date: End date.
    """

    start_month: tuple[int, int] = start_date.year, start_date.month
    end_month: tuple[int, int] = end_date.year, end_date.month

    if start_month == end_month:
        return [start_month]
    if start_month != end_month:
        return [start_month, end_month]
    return None


@st.cache_data(show_spinner='Lejupielādē un apstrādā datus...', show_time=True)
def load_and_parse_data(
    months: list[tuple[int, int]],
) -> pl.LazyFrame:
    """
    Download and extract zip file from the given URL.
    Parse the contents of zip file to polars LazyFrame

    Args:
        months: list of months (as (year, month) tuples) to download data for.
        Can be acquired from get_months() function
        by passing start_date and end_date values
    """

    urls: list[str] = []
    lazy_frames: list[pl.LazyFrame] = []

    for month in months:
        url = available_months.url(month[0], month[1])
        if url:
            urls.append(url)

    for url in urls:
        with tempfile.NamedTemporaryFile(
            delete_on_close=False, suffix='.zip'
        ) as temp_file:
            with requests.get(url, timeout=30, stream=True) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)

            temp_file.close()

            with tempfile.TemporaryDirectory() as temp_dir:
                extract_dir = pathlib.Path(temp_dir)
                with zipfile.ZipFile(temp_file.name, mode='r') as archive:
                    archive.extractall(extract_dir)
                for file_path in extract_dir.rglob('*'):
                    if file_path.is_file():
                        lazy_frame = pl.read_csv(file_path).lazy()
                        lazy_frames.append(lazy_frame)

            pathlib.Path(temp_file.name).unlink()

    lazy_frame = pl.concat(lazy_frames, how='vertical')

    return lazy_frame
