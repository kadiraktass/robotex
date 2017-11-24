 #!/bin/bash



echo "--- wait"
#test for internet: 
#but we might not have internet, but still need to run. 10+ second delay is not too long?

for i in {1..50}
do
	httping -aqc 1 http://google.com && echo "WE HAVE CONNECTION" && break 
	sleep 1
	echo "loop"
	echo -n ${i} 
done


echo "--- start"

#git pull
#Btw, git user is roboteer and pass is roboteer2017
# Robotiklubi24 Labor001
git fetch --all
git reset --hard origin/master


cd software
python main.py --id=AZ --brakes=on --target=blue


echo "--- finish"
read -p "Press any key to finish" -n1 -s
echo