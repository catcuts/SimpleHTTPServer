#!/usr/bin/bash

HOST=192.168.116.160
USER=root
PASSWD=@^hly012501_Pi31415926$

while getopts "h:" arg  # 选项后面的冒号表示该选项需要参数
do
    case $arg in
        h)
            HOST=$OPTARG  # 参数存在 $OPTARG 中
            ;;
    esac
done

curl -u $USER:$PASSWD $HOST:5000/getNetworkConf | python -m json.tool
