
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
	# docker$B%0%k!<%W$,$J$1$l$P:n$k(B
	sudo groupadd docker
	# $B8=9T%f!<%6$r(Bdocker$B%0%k!<%W$K=jB0$5$;$k(B
	sudo gpasswd -a $USER docker
	# docker$B%G!<%b%s$r:F5/F0$9$k(B (CentOS7$B$N>l9g(B)
	sudo systemctl restart docker
	# exit$B$7$F:F%m%0%$%s$9$k$HH?1G$5$l$k!#(B
	exit
}
$1
