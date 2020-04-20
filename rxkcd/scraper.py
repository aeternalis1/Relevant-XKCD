from bs4 import BeautifulSoup
from .models import Comic
from .utils import clean_text
from .update_db import update_wordbank_many, update_comics_many, update_url, update_title, update_og_title, update_og_ttext
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
	try:
		return res.text
	except:
		return "[Title unavailable]"


#gets title text of comic as uncleaned string
def get_ttext(comic_num):
	URL = "https://www.xkcd.com/%s" % str(comic_num)
	soup = make_soup(URL)
	if soup == None:
		return "Error: comic %d not found" % comic_num
	res = soup.find("img", {"src": re.compile(r"imgs\.xkcd\.com/comics/")})
	try:
		return res['title']
	except:		# title text unavailable? take it from ExplainXKCD
		URL2 = "https://www.explainxkcd.com/wiki/index.php/%s" % str(comic_num)
		soup2 = make_soup(URL2)
		for span in soup2.find_all("span"):
			if span.text == 'Title text:':
				cur = span.parent
				return " ".join(cur.text.split()[2:])
		return "[Title text unavailable]"


def get_info(comic_num):
	URL = "https://www.explainxkcd.com/wiki/index.php/%s" % str(comic_num)
	soup = make_soup(URL)
	if soup == None:
		return "Error: comic %d not found" % comic_num

	result = Comic(comic_num)

	# get title
	result.og_title = get_title(comic_num)
	result.title = clean_text(result.og_title)

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
	result.og_ttext = get_ttext(comic_num)
	result.title_text = clean_text(result.og_ttext.split())

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
		wordbank[word] = sorted(wordbank[word], reverse = True)[:min(20,len(wordbank[word]))]

	update_wordbank_many(wordbank)
	update_comics_many(comics)


def add_urls():
	for i in range(1, num_xkcd+1):
		update_url(i, get_img_url(i))


def add_titles():
	for i in range(1, num_xkcd+1):
		update_title(i, clean_text(get_title(i).split()))


def add_og_titles():
	for i in range(1, num_xkcd+1):
		update_og_title(i, get_title(i))


def add_og_ttexts():
	for i in range(1, num_xkcd+1):
		update_og_ttext(i, get_ttext(i))

'''
if __name__ == "__main__":
	add_og_titles()
	add_og_ttexts()
'''