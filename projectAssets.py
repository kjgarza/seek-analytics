__author__ = 'kristian'

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello World'


@app.route('/get')
  def get(self):
    template_values={'principal':'1000','rate':'10'}
    # render the page using the template engine
    path = os.path.join(os.path.dirname(__file__),'index.html')
    self.response.out.write(template.render(path,template_values))




if __name__ == "__main__":
    app.run()


