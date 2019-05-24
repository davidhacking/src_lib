sudo kill -9 `cat rsyncd.pid`
sudo rm -f rsyncd.pid
rsync -4 --daemon --config=/home/shiwei/rsync_server/rsyncd.conf --port=9527
