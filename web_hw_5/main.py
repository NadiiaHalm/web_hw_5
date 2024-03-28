import sys
import json
import platform
from typing import Any
from datetime import datetime, timedelta

import aiohttp
import asyncio


class HttpError(Exception):
    pass


class SelfError(Exception):
    pass


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    raise HttpError(f"Error status: {resp.status} for {url}")
        except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
            raise HttpError(f'Connection error: {url}', str(err))


def save_to_json(data: list[dict[Any, dict[str, dict[str, Any] | dict[str, Any]]]]):
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def main(index_days):
    data = []
    index_days = int(index_days)
    if index_days > 10:
        raise SelfError(f"Index {index_days} can't be greater than 10!")
    else:
        while index_days > -1:
            d = datetime.now() - timedelta(days=index_days)
            index_days -= 1
            shift = d.strftime('%d.%m.%Y')
            try:
                response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
                date = {response['date']: {'EUR': {'sale': response['exchangeRate'][8]['saleRate'],
                                                   'purchase': response['exchangeRate'][8]['purchaseRate']},
                                           'USD': {'sale': response['exchangeRate'][23]['saleRate'],
                                                   'purchase': response['exchangeRate'][23]['purchaseRate']}}
                        }
                data.append(date)
            except HttpError as err:
                print(err)
                return None
        save_to_json(data)
        return data


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(sys.argv[1]))

