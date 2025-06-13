import asyncio
from typing import List, Dict

import httpx


class Item:
	def __init__(self, response: Dict):
		self.type: str = response.get('type')
		self.name: str = response.get('name')
		self.id: int = response.get('id')
		self.price = {
			'currency': response.get('currency'),
			'initial': response.get('initial'),
			'final': response.get('final'),
		}
		self.tiny_image: str = response.get('tiny_image')
		self.metascore: int = response.get('metascore')
		self.platforms = {
			'windows': response.get('windows'),
			'mac': response.get('mac'),
			'linux': response.get('linux'),
		}
		self.streamingvideo: bool = response.get('streamingvideo')


class SteamResponse:
	def __init__(self, total: int, items: List[Item]):
		self.total: int = total
		self.items: List[Item] = items


async def search_for_game(
	query: str,
	country: str = 'de',
	lang: str = 'en',
	timeout: float = 5.0,
) -> SteamResponse:
	url = 'https://store.steampowered.com/api/storesearch'
	params = {
		'term': query,
		'cc': country,
		'l': lang,
	}
	async with httpx.AsyncClient(timeout=timeout) as client:
		try:
			resp = await client.get(url, params=params)
			resp.raise_for_status()
		except httpx.RequestError as exc:
			raise Exception(f'Network error: {exc}')
		except httpx.HTTPStatusError as exc:
			raise Exception(f'Bad response ({exc.response.status_code}): {exc}')

		resp = resp.json()

		items: List[Item] = []

		for listing in resp.get('items'):
			items.append(Item(listing))

		return SteamResponse(resp.get('total'), items)


if __name__ == '__main__':
	data = asyncio.run(search_for_game('Factorio'))
	for item in data.items:
		print(item.id)
		print(item.name)
		print(item.tiny_image)
