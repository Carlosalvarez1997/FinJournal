from flask_app import app
from flask_app.controllers import user
import requests





if __name__ == "__main__":
    app.run(debug=True, host = "localhost", port = 6001)
