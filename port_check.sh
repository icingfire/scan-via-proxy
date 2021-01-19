#!/bin/bash
# $1  ip
# $2  port

function port_check()
{
    ip=$1
    port=$2
/usr/bin/expect <<EOF
    set timeout 15 
    spawn telnet $ip $port
    expect {
        "Connection closed" { exit 1 }
        "Connection refused" { exit 1 }
        "Unable to connect to" { exit 1 }
        eof
    }
EOF
    return $? 
}

port_check $1 $2 >>./port_chk.log && echo "$1 $2 port open"
