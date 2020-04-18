from bs4 import BeautifulSoup
from .models import Comic
from .utils import clean_text
from .update_db import update_wordbank_many, update_comics_many, update_url, update_title
import re
import requests
import time

def make_soup(url):
    try:
        html = requests.get(url).content
    except:
        return None
    return BeautifulSoup(html, features="html.parser")


# gets image url for comic
def get_img_url(comic_num):
	URL = "https://www.xkcd.com/%s" % str(comic_num)
	soup = make_soup(URL)
	if soup == None:
		return "Error: comic %d not found" % comic_num
	res = str(soup.find(text=re.compile(r"Image URL \(for hotlinking/embedding\):"))).strip('\n')
	return res[res.find("https"):].strip()


# gets title of comic as uncleaned string
def get_title(comic_num):
	URL = "https://www.xkcd.com/%s" % str(comic_num)
	soup = make_soup(URL)
	if soup == None:
		return "Error: comic %d not found" % comic_num
	res = soup.find("div", {"id": "ctitle"})
	return res.text


#gets title text of comic as uncleaned string
def get_ttext(comic_num):
	URL = "https://www.xkcd.com/%s" % str(comic_num)
	soup = make_soup(URL)
	if soup == None:
		return "Error: comic %d not found" % comic_num
	res = soup.find("img", {"src": re.compile(r"imgs\.xkcd\.com/comics/")})
	return res['title']


def get_info(comic_num):
	URL = "https://www.explainxkcd.com/wiki/index.php/%s" % str(comic_num)
	soup = make_soup(URL)
	if soup == None:
		return "Error: comic %d not found" % comic_num

	result = Comic(comic_num)

	# get title
	result.title = clean_text(get_title(comic_num).split())

	# get transcript
	transcript = soup.find("span", {"id":"Transcript"})
	result.transcript = []
	cur = transcript.parent
	while cur:
		if cur.name == 'dl':
			for dd in cur:
				result.transcript.append(str(dd).strip('<dd>').strip('</dd>'))
		elif cur.name == 'span':
			break
		cur = cur.nextSibling
	result.transcript = clean_text((" ".join(result.transcript)).split())

	# get title text
	for span in soup.find_all("span"):
		if span.text == 'Title text:':
			cur = span.parent
			result.title_text = clean_text(cur.text.split())

	# get explanation 
	explanation = soup.find("span", {"id":"Explanation"})
	result.explanation = []
	cur = explanation.parent
	while cur:
		if cur.name == 'p':
			result.explanation.append(cur.text)
		elif cur.name == 'span':
			break
		cur = cur.nextSibling
	result.explanation = clean_text((" ".join(result.explanation)).split())

	# get image URL
	result.img_url = get_img_url(comic_num)

	return result


num_xkcd = 2295


# gets comics and wordbank
# initially wordbank just stores words and comics in which that word appear (along with # of occurrences)
def scrape_pages():
	comics = {}
	wordbank = {}
	for i in range(1, num_xkcd+1):
		try:
			comic = get_info(i)
			words = {}
			for word in comic.title + comic.transcript + comic.title_text + comic.explanation:
				if word in words:
					words[word] += 1
				else:
					words[word] = 1
			for word in words:
				if word in wordbank:
					wordbank[word].append([words[word], comic.id])
				else:
					wordbank[word] = [[words[word], comic.id]]
			comics[comic.id] = comic
		except:
			continue

	for word in wordbank:
		wordbank[word] = sorted(wordbank[word], reverse = True)

	update_wordbank_many(wordbank)
	update_comics_many(comics)


def add_urls():
	for i in range(1, num_xkcd+1):
		update_url(i, get_img_url(i))


def add_titles():
	for i in range(1, num_xkcd+1):
		update_title(i, get_title(i))


if __name__ == "__main__":
	print(get_ttext(1))