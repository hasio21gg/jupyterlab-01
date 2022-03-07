
proc1(){
	#
	sudo apt-get update
	#
	sudo apt-get install \
		apt-transport-https \
		ca-certificates \
		curl \
		gnupg2 \
		software-properties-common
#
curl -fsSL \
	https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null


sudo apt-get install docker-ce docker-ce-cli containerd.io
#
apt-cache madison docker-ce
#
sudo docker run hello-world
}
proc2(){
	sudo curl -L --fail \
		https://raw.githubusercontent.com/linuxserver/docker-docker-compose/master/run.sh \
		-o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
}
proc3(){
	mkdir ~/docker
}
proc4(){
	# dockerグループがなければ作る
	sudo groupadd docker
	# 現行ユーザをdockerグループに所属させる
	sudo gpasswd -a $USER docker
	# dockerデーモンを再起動する (CentOS7の場合)
	sudo systemctl restart docker
	# exitして再ログインすると反映される。
	exit
}
$1
