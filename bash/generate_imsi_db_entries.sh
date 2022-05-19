#!/bin/bash
for id in {1..99}
do
	if [ $((id)) -lt 10 ]; then
		id="0$id"
	fi
	echo "INSERT INTO \`users\` VALUES ('20899000074$id','380561234567','55000000000001',NULL,'PURGED',50,40000000,100000000,47,0000000000,1,0xfec86ba6eb707ed08905757b1bb44b8f,0,0,0x40,'ebd07771ace8677a',0xc42449363bbad02b66d16bc975d77cc1);"
done
