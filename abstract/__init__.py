from flask import Flask, request, jsonify, redirect, url_for
from newspaper import Article
from xml.etree  import ElementTree
from BeautifulSoup import BeautifulSoup
from flask.ext.cors import CORS, cross_origin
from urlparse import urljoin

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Debug logging
import logging
import sys

# Defaults to stdout
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
try:
  log.info('Logging to console')
except:
  _, ex, _ = sys.exc_info()
  log.error(ex.message)

@app.route('/')
@cross_origin()
def index():
  url_to_clean = request.args.get('url')
  if not url_to_clean:
      return jsonify(status='up')

  article = Article(url_to_clean)
  article.download()
  article.parse()

  try:
    html_string = ElementTree.tostring(article.clean_top_node)
  except:
    html_string = "Error converting html to string."

  try:
    article.nlp()
  except:
    log.error("Couldn't process with NLP")

  try:
    html = BeautifulSoup(html_string)

    links = html.findAll('a')
    hrefs = [link.get('href') for link in links if link.get('href')]
    hrefs = [urljoin(url_to_clean, href) for href in hrefs]
    hrefs = [href for href in hrefs if url_to_clean not in href]

    for link in links:

      if link.get('href'):
        link['href'] = urljoin(url_to_clean, link['href'])
        if url_to_clean in link['href']:
          link.replaceWithChildren()

    html_string = str(html)
  except:
    hrefs = []
    log.error("Couldn't get hrefs")

  try:
    html = BeautifulSoup(article.html)
    title = html.title.string
  except:
    title = article.title
    log.error("Couldn't get title")

  data = {
    'html': html_string,
    'hrefs': hrefs,
    'authors': str(', '.join(article.authors)),
    'title': title,
    'text': article.text,
    'publish_date' : article.publish_date,
    'top_image': article.top_image,
    'videos': str(', '.join(article.movies)),
    'keywords': str(', '.join(article.keywords)),
    'summary': article.summary,
    'url': url_to_clean
  }

  return jsonify(**data)

