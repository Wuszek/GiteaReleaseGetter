# Gitea releaseGetter

### Description
This script, run periodically, should automatically check for new release of Gitea on github and make all necessary
changes to update spksrc build files and prepare for Synology package update.

### Built With
* python3
* [discord.sh](https://github.com/ChaoticWeg/discord.sh) - bash integration for Discord webhooks

### Requirements
```bash
sudo apt install python3 -y
pip3 install requests
sudo apt install bats curl jq -y
```

### How to run 
Script has no loop, so it should be run periodically using built-in scheduler.

```bash
python3 main.py
```

### Flow diagram

![Flow diagram](media/diag.png "Flow diagram")
* Green - DONE 
* Light yellow - IN PROGRESS
* Yelow - PLANNED
---
### Work still in progress.