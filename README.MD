# Game Of Cards bot for Telegram

## Setup

Create a new Telegram bot via @BotFather.

Install all needed packages from `requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create file `botConfig.py` where you should specify your bot token, proxy, etc.

```python
# -*- coding: utf-8 -*-
botToken=""
telebotProxy={'https':'socks5h://'}
```

Create file `cards.py` where you store database of texts for your cads:
```python
cards = {
	"default set":{
		"white": [
			"White card 1",
			"White card 2",
			...
			],
		"black": [
			"Black card 1",
			"Black card 2",
			...
			],
		"black2": [
			"Black card with 2 spaces",
			...
			]
		}
}
```

## Run

Start the bot by running `bot.py`
```
python bot.py
```
