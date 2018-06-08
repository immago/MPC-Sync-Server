## MPCHC-Sync-Server

### Configuration
Change variables in *start.sh* file

### Install as service
Example: init.d.example
```
sudo nano /etc/init.d/mpc-hc-sync
sudo chmod +x /etc/init.d/mpc-hc-sync
sudo update-rc.d mpc-hc-sync defaults
```
__start or stop service__
```
sudo /etc/init.d/mpc-hc-sync start
sudo /etc/init.d/mpc-hc-sync stop
```
