from abstract import app
from abstract.controllers import article

if __name__ == '__main__':
  app.register_blueprint(article.mod)
  app.run(debug=True)
