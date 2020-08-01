from flup.server.fcgi import WSGIServer
from api import app

if __name__ == "__main__":
	# WSGIServer(app, bindAddress=('localhost', 9000)).run()
	WSGIServer(app, bindAddress='/tmp/zk-monitor-data-api-fcgi.sock').run()
