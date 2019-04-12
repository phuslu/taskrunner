## taskrunner
a task runner for our cron jobs

### Configuraion
see [development.toml](development.toml)

### Installation
```bash
  sudo apt install python-pip3
  sudo pip3 install pipenv
  env PIPENV_VENV_IN_PROJECT=1 pipenv install
```

### Start Cron Daemon
```bash
  pipenv run python cron.py
```

### Start As Daemon
```bash
  echo ENV=production-usa | sudo tee .env
  pipenv run supervisord
  pipenv run supervisorctl start cron
```
