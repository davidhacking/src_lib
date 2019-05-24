rm rsyncd.pid
ps x | grep rsync | grep -v grep | awk '{print $1}' | xargs kill -9
rsync -4 --daemon --config=$HOME/rsync_server/rsyncd.conf --port=9527
