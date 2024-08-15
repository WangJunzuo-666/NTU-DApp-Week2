from flask import Flask, render_template, request

app=Flask(__name__)

@app.route('/', methods=["get", "post"])

def index():
  return render_template("index.html")

if __name_=="__main__"
  app.run()
