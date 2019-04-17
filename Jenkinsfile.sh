#!/bin/bash

set -xe

DIRECTORY="$(cd "$(dirname "$0")"; pwd -P)"
PROJECT=$(basename "${DIRECTORY}")

cd "${DIRECTORY}"

# checking
python3.6 -m compileall .
rm -rf __pycache__

# changelog
git log --oneline --pretty=format:"%h %s" -5 | tee CHANGELOG

# script file
SHELLSCRIPT=$(mktemp)
trap "rm -f ${SHELLSCRIPT}" EXIT

# deploy
REMOTE=/opt
IPLIST=$(echo ${IP} | sed 's/,/ /g')
for IP in ${IPLIST}
do
	IP=$(echo ${IP} | egrep -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
	case ${IP} in
	    * )
	        ENV=production-usa
	        ;;
	esac
	echo IP=${IP}, ENV=${ENV}
	# setup pipenv
	cat <<EOF > ${SHELLSCRIPT}
		set -ex
		if ! hash pipenv; then
			if uname -a | grep -q -w Ubuntu; then
				# Ubuntu 16
				sudo add-apt-repository -y ppa:jonathonf/python-3.6
				sudo apt-get update -y
				sudo apt-get install -y python3.6 python3.6-dev
				sudo pip3 install pipenv
			elif uname -r | grep -q -w el7; then
				# CentOS 7
				sudo yum install -y python36-devel python36-pip git
				sudo pip3.6 install pipenv
			else
				echo 'Please install pipenv !!!'
				exit 1
			fi
		fi
		sudo mkdir -p ${REMOTE}/${PROJECT}
		sudo mkdir -p ${REMOTE}/${PROJECT}
		sudo chown -R \$(whoami) ${REMOTE}/${PROJECT}
		sudo chown -R \$(whoami) ${REMOTE}/${PROJECT}
EOF
	ssh -F ssh_config ${IP} < ${SHELLSCRIPT}
	# rsync folder
	rsync -avz . -e "ssh -F ssh_config" ${IP}:${REMOTE}/${PROJECT}/
	# install pipenv dependencies
	cat <<EOF > ${SHELLSCRIPT}
		set -ex
		cd ${REMOTE}/${PROJECT}
		cd ${REMOTE}/${PROJECT}
		env PIPENV_VENV_IN_PROJECT=1 pipenv install
		echo ENV=${ENV} | tee .env
EOF
	ssh -F ssh_config ${IP} < ${SHELLSCRIPT}
done
