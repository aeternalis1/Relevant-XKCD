from rxkcd import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)