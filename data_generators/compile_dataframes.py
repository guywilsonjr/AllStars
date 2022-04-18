import asyncio
import os
from io import BytesIO

import pandas as pd
from aiofile import async_open

career_df_loc = '/tmp/allstar/data/ncaa/player/career'
yearly_df_loc = '/tmp/allstar/data/ncaa/player/yearly'


def fns(fp: str):
    return [fn for fn in os.listdir(fp)]

async def get_file_data(fn):
    async with async_open(fn, "rb") as afp:
        return BytesIO(await afp.read())

async def async_get_file_data(fns):
    return await asyncio.gather(*[get_file_data(fn) for fn in fns])

def get_pdfstr_lists(fns):
    return asyncio.run(async_get_file_data(fns))

async def recursive_concat(fns):
    df_size = len(fns)
    midpoint = df_size // 2
    if df_size > 2:
        d0 = await recursive_concat(fns[midpoint:])
        d1 = await recursive_concat(fns[:midpoint])
        d0.extend(d1)
        return [pd.concat(d0)]

    elif df_size == 2:
        f0 = fns[0]
        f1 = fns[1]

        if isinstance(fns[0], str):
            f0 = pd.read_csv(await get_file_data(fns[0]))

        if isinstance(fns[1], str):
            f1 = pd.read_csv(await get_file_data(fns[1]))

        return [pd.concat([f0, f1])]
    elif df_size == 1:
        f0 = fns[0]
        if isinstance(fns[0], str):
            f0 = pd.read_csv(await get_file_data(fns[0]))
        return [f0]


def create_files():
    career_fns = [f'{career_df_loc}/{fn}' for fn in os.listdir(career_df_loc)]
    yearly_fns = [f'{yearly_df_loc}/{fn}' for fn in os.listdir(yearly_df_loc)]


    career_dfs = asyncio.run(recursive_concat(career_fns))
    yearly_dfs = asyncio.run(recursive_concat(yearly_fns))

    pd.concat(career_dfs).to_csv('ncaa-players-2010-2021-career.csv')
    pd.concat(yearly_dfs).to_csv('ncaa-players-2010-2021-yearly.csv')

create_files()
