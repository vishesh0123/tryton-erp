To setup centralised Erp system we need postgresdb
Create a new user with password
create new database with any name of your choice
I have done this on mac using psql command line tool , you can ask chat gpt to do all this things in your OS..

also make sure you have latest version of python installed

1.Clone this repo to your local repo
```
git clone https://github.com/vishesh0123/tryton-erp
```

2. Go to centralised-erp-folder
3. Install all dependencies

```
pip install -r requirements.txt
```

4. Change trytond.conf file

```
uri = postgresql://username:password@localhost:5432/
```
update username and pasword there

5. Initializing database in tryton (replace '<database name>' with your database name )

```
trytond-admin -c trytond.conf -d <database name> --all
```

6. Activate stock and inventory module

```
trytond-admin -c trytond.conf -d <database name> -u stock --activate-dependencies
```

7. Start the server
```
trytond -c trytond.conf
```

8. Update dbconf.py with your updated db configuration

9. Setup Db for metrics table
```
python3 db-setup.py
```
10. Run Script to automate inventory setup

```
python3 automate-inventory.py
```

11. While this script is running , open new terminal to run metrics GUI

```
python3 gui-metrics.py
```



