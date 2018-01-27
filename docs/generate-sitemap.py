"""Create sitemap for HTML files."""
# Standard Library
import os
import stat
from datetime import date

# Pyramid
import jinja2


TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for file in files %}
  <url>
    <loc>{{ site }}{{ file.path }}</loc>
    <lastmod>{{ file.lastmod }}</lastmod>
   </url>
{% endfor %}
</urlset>
""".strip()

env = jinja2.Environment()

sitemap_files = []

os.chdir("build")

for root, dirs, files in os.walk(".", topdown=False, followlinks=True):
    for name in files:

        if root.startswith("./doctrees") or root.startswith(("./epub")):
            continue

        if name.endswith(".html"):
            path = os.path.join(root, name)
            statbuf = os.stat(path)
            fdate = date.fromtimestamp(statbuf[stat.ST_MTIME])
            lastmod = fdate.strftime('%Y-%m-%d')

            path = path[len("."):]
            path = path.replace("/html/", "/docs/")

            sitemap_files.append(dict(path=path, lastmod=lastmod))

template = env.from_string(TEMPLATE)
doc = template.render(files=sitemap_files, site="https://websauna.org")
print(doc)
