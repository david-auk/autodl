# autodl-py
automaticly download latest video
Translated script of [THIS](https://github.com/david-auk/autodl) github project
### Installation:

```bash
pip3 install -r requirements.txt
```

```bash
python3 install.py
```

### Use:

```bash
python3 main.py
```

### Dependencies:
* mariadb-server
* ffmpeg

## Functions Documantation

### initialising functions.py

##### importing

```python
import funcitons
```
> note: must be within project dir

### Data management:

#### Getting data

##### code:
```python
functions.getData("table_name", "target_colomn_name", "target_colomn_value")
```
> return: The cursor data

##### example:
```python
functions.getData("account", "id", 'UC-lHJZR3Gqxm24_Vd_AJ5Yw')
myCursorChannelRequest = functions.getDataCursor
for (channelTitle, id, priority) in myCursorChannelRequest:
	print(channelTitle)
	print(id)
	print(priority)
```

#### Entry checking

##### code:
```python
functions.entryExists("table_name", "id_value")
```
> return: The cursor data

##### example:
```python
entryExists = functions.getDataContentCheck("content", urlid)
if enteryExist:
	print("the entery exists!")
```
> note: The reason this is a seperated function is because the *getDataContentCheck* uses an other cursor then *getData*, this way it can be used within the checkloop in main.py

### Messaging via Telegram:

#### Messaging host

##### code:
```python
functions.msgHost("query")
```
> send query to the host

##### example:
```python
functions.msgHost("Hello, World!")
```

#### Messaging everyone

##### code:
```python
functions.msgAll("query")
```
> send query to all the chatId's in the secret dictionary

##### example:
```python
functions.msgAll("Hello, World!")
```