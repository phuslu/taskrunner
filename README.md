## taskrunner
a task runner for our cron jobs

### Configuraion
see [development.toml](development.toml)

### Deploy
```bash
  IP=<IP> ./Jenkinsfile.sh
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
