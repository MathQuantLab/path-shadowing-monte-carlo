import io
import os
from datetime import datetime

import aiohttp
import async_lru
import pandas as pd


@async_lru.alru_cache(maxsize=32, typed=False, ttl=3600)
async def fetch_ticker_data(
    ticker: str = "^GSPC",
    *,
    quote: bool = False,
    start: str | datetime = None,
    end: str | datetime = None,
    wsj: bool = False,
) -> pd.DataFrame:
    """Gather data from Yahoo Finance API

    Args:
        ticker (str, optional): ticker. Defaults to "^GSPC".
        quote (bool, optional): if True, get the current quote, else historical values. Defaults to False.
        start (str | datetime, optional): start date. Defaults to None.
        end (str | datetime, optional): end date. Defaults to None.
        wsj (bool, optional): if True, get data from Wall Street Journal. Defaults to False.

    Raises:
        ValueError: if Wall Street Journal data is requested for a ticker different than ^GSPC
        ValueError: if end date is less than start date
        ValueError: if failed to fetch data from the API

    Returns:
        pd.DataFrame: DataFrame with the data
    """
    if not quote:
        if start and isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d")
        if end and isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d")

        if end and start and end < start:
            raise ValueError("End date must be greater than start date")

    if wsj and ticker != "^GSPC":
        raise ValueError("Wall Street Journal data is only available for ^GSPC ticker")

    if wsj:
        path = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            "Data",
            "HistoricalPrices_SPX.pkl",
        )
        df: pd.DataFrame = pd.read_pickle(path)
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]
        return df

    url = f"https://financial-data.shriimpe.fr/api/ticker/history/{ticker}"

    if not quote:
        if start:
            url += f"?start_date={start.strftime('%Y-%m-%d')}"
        if end:
            url += f"{'&' if '?' in url else '?'}end_date={end.strftime('%Y-%m-%d')}"
    else:
        url += f"?start_date={datetime.today().strftime('%Y-%m-%d')}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Accept": "python/pickle"}) as response:
            if response.status != 200:
                print(response.status)
                raise ValueError(
                    f"Failed to fetch data from {url} with status {response.status}",
                    f"Error message: {await response.text()}",
                )
            df = pd.read_pickle(io.BytesIO(await response.read()))

    return df
