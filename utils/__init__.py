import asyncio
import functools
import io
import os
from datetime import datetime
from typing import Any, Dict

import aiohttp
import async_lru
import pandas as pd
import yaml


@functools.cache
def get_config() -> Dict[str, Any]:
    """Reads the configuration file

    Returns:
        Dict[str, Any]: content of the file
    """
    with open("env.yml") as f:
        return yaml.safe_load(f)


@async_lru.alru_cache(maxsize=32, typed=False, ttl=3600)
async def fetch_ticker_data(
    *tickers: str,
    wsj: bool = False,
    quote: bool = False,
    start: str | datetime = None,
    end: str | datetime = None,
) -> pd.DataFrame | Dict[str, pd.DataFrame]:
    """Gather data from Yahoo Finance API

    Args:
        tickers (str, optional): list of tickers. Defaults to "^GSPC".
        wsj (bool, optional): if True, get data from Wall Street Journal (only after 1978). Defaults to False.
        quote (bool, optional): if True, get the current quote, else historical values. Defaults to False.
        start (str | datetime, optional): start date. Defaults to None.
        end (str | datetime, optional): end date. Defaults to None.

    Raises:
        ValueError: if Wall Street Journal data is requested for a ticker different than ^GSPC
        ValueError: if end date is less than start date
        ValueError: if failed to fetch data from the API

    Returns:
        pd.DataFrame | Dict[str, pd.DataFrame]: DataFrame with the data
    """
    if not quote:
        if start and isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d")
        if end and isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d")

        if end and start and end < start:
            raise ValueError("End date must be greater than start date")

    if wsj and tickers and "^GSPC" not in tickers:
        raise ValueError("Wall Street Journal data is only available for ^GSPC ticker")

    if wsj:
        path = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            "data",
            "HistoricalPrices_SPX.pkl",
        )
        df: pd.DataFrame = pd.read_pickle(path)
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]
        return df

    if not tickers:
        tickers = ("^GSPC",)

    async def __process_request(ticker: str) -> pd.DataFrame:
        """Process the request to the Yahoo Finance API

        Args:
            ticker (str): ticker to fetch data from

        Raises:
            ValueError: if failed to fetch data from the API

        Returns:
            pd.DataFrame: result
        """
        endpoint = "quote" if quote else "history"
        url = f"{get_config()['data_endpoint']}ticker/{endpoint}/{ticker}"

        if not quote:
            if start:
                url += f"?start_date={start.strftime('%Y-%m-%d')}"
            if end:
                url += (
                    f"{'&' if '?' in url else '?'}end_date={end.strftime('%Y-%m-%d')}"
                )
        else:
            url += f"?start_date={datetime.today().strftime('%Y-%m-%d')}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers={"Accept": "python/pickle"}
            ) as response:
                if response.status != 200:
                    raise ValueError(
                        f"Failed to fetch data from {url} with status {response.status}",
                        f"Error message: {await response.text()}",
                    )
                df = pd.read_pickle(io.BytesIO(await response.read()))
                return df

    if len(tickers) == 1:
        return await __process_request(tickers[0])
    else:
        return dict(
            zip(
                tickers,
                await asyncio.gather(
                    *[__process_request(ticker) for ticker in tickers]
                ),
            )
        )
