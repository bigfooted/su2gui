# start environment:
$ export PATH="/home/nijso/anaconda3/bin:$PATH"
$ source activate pv-env


# run as server:
$ python su2gui_su2.py --port 8888 --host='0.0.0.0' --server


create docker:
docker build -t trame-su2gui-app . &> build.log
docker run -it --rm -p 8888:80 trame-su2gui-app


check docker container:
docker ps
docker exec -it 1313b9788f54 /bin/bash

