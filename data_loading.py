"""
Data loading functions to download and extract .zip file
based on url from month_data.py.
"""

import datetime
import io
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

    files_dict: dict[str, io.StringIO] = {}
    urls: list[str] = []
    lazy_frames: list[pl.LazyFrame] = []

    for month in months:
        url = available_months.url(month[0], month[1])
        if url:
            urls.append(url)

    for url in urls:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content), mode='r') as archive:
            for file in archive.namelist():
                if file.endswith('/'):
                    continue
                raw_bytes = archive.read(file)
                text_str = raw_bytes.decode(encoding='utf-8')
                files_dict[file] = io.StringIO(text_str)

    for csv_io in files_dict.values():
        df = pl.read_csv(csv_io)
        lazy_frames.append(df.lazy())

    lazy_frame: pl.LazyFrame = pl.concat(lazy_frames)

    return lazy_frame
