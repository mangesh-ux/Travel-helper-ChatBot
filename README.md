
# Travel Helper ChatBot

The idea of this chatbot is to make travel planning an easy process while this chatbot answers all your crucial questions by the knowledge collected through publically avaialable APIs.


## How to run the app?

Create a python3 environment (<=3.8.x)

```bash
  python3 -m venv venv
```

Activate environment

```bash
  source venv/bin/activate
```
Keyword "source" is not required for windows users.

Install Requirements

```bash
  pip3 install -r requirements.txt
```
Add your API keys in `actions/.env`.
In the project directory, first create a folder `models`. Open two terminals with virtual environment activated, In the first tab run:

```bash
  rasa train && rasa run -m models --enable-api --cors '*'
```
running `rasa train` is only required once for training the model.

In the second tab run:

```bash
   cd actions && rasa run actions
```
After both rasa and action server are up and running, open `index.html` in the browser.

Open `graph.html` to visualize working of rasa core for this chatbot.
## Youtube Demo

[![yt_image](https://imgur.com/9rx0w5r.png)](https://youtu.be/MCboRcJxsFk)

