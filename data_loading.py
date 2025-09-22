"""
Data loading functions to download and extract .zip file
based on url from month_data.py.
"""

import datetime
import io
import zipfile

import requests
import streamlit as st


def get_months(
    start_date: datetime.date, end_date: datetime.date
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
    elif start_month != end_month:
        return [start_month, end_month]
    else:
        return None


@st.cache_data(show_spinner='Lejupielādē datus...')
def load_data(url: str) -> dict[str, io.BytesIO]:
    """
    Download and extract zip file from the given URL.

    Args:
        url: URL to download the zip file from.
    """

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    files_dict: dict[str, io.BytesIO] = {}

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        for filename in zip_file.namelist():
            if not filename.endswith('/'):
                files_dict[filename] = io.BytesIO(zip_file.read(filename))

    return files_dict
