from flask import Flask, render_template
app = Flask(__name__)

# For controller routes
from controllers import *

# For creating tables
from models import *

# For third party packages
from extensions import *
