default=install

install:
		sudo pip3 install -r requirements.txt
		chmod +x ferdowsi.py
		sudo cp ferdowsi.py /usr/bin/ferdowsi