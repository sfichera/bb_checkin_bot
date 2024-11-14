#!/bin/bash
ps -ef | grep bb_checkin_bot | grep -v grep | awk '{print $2}' | xargs sudo kill -9