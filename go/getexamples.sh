#!/bin/sh

getexheadfirstgo() {
	git clone https://github.com/headfirstgo/greeting.git
	git clone https://github.com/headfirstgo/prose.git
	git clone https://github.com/headfirstgo/gadget.git
	git clone https://github.com/headfirstgo/calendar.git
	git clone https://github.com/headfirstgo/magazine.git
	git clone https://github.com/headfirstgo/datafile.git
	git clone https://github.com/headfirstgo/keyboard.git
}

HEADFIRSTGO_DIR="headfirstgo"
echo "mkdir ${HEADFIRSTGO_DIR}; cd ${HEADFIRSTGO_DIR}; getexheadfirstgo"
