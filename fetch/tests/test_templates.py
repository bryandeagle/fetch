from jinja2 import Environment
import os

TEMPLATES_DIR = 'app/templates'
env = Environment(autoescape=True)

for file in os.listdir(TEMPLATES_DIR):
    full_file = os.path.join(TEMPLATES_DIR, file)
    with open(full_file) as template:
        env.parse(template.read())
