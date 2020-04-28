# Relevant-XKCD

Finds a relevant XKCD based on keywords

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
* [MongoDB](https://www.mongodb.com/) - Database for comics and wordbank
* [spaCy](https://spacy.io/) and [nltk](https://www.nltk.org/) - Used to determine comic relevance

## Deployment

This project can be found [here](https://rxkcd.herokuapp.com), deployed on Heroku. A few notes:
* First bootup can be particularly slow and might crash, since the app idles after a certain length of disuse.
* Long queries (in terms of number of keywords) can cause the app to crash because workers time out after 30 seconds without response.

## Installation

To run this project on your own machine, clone this repository and install the [requirements](requirements.txt) (`pip install -r requirements.txt`. Then, in `rxkcd/instance` add a `config.py` file with a `SECRET_KEY` (any collection of random bytes will do) and a `MONGO_URI` (to connect to your own MongoDB database).

To populate this database, navigate to the `rxkcd/scraper.py` file and change `num_xkcd` to the latest released comic number, and call the function `scrape_pages()` by running `python scraper.py` inside the `rxkcd` directory. Note that you may have to remove the dots preceding imports (due to relative imports not working in scripts) in the `scraper.py` and `update_db.py` files, but make sure to re-add them after populating your database.

Then the app can be run by calling `python app.py`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
