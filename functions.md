#Functions.py Documantation

## initialising functions.py

#### importing

```python
import funcitons
```
> note: must be within project dir

## Use:

### Getting data

#### code:
```python
functions.getData("table_name", "target_colomn_name", "target_colomn_value")
```
> return: The cursor data

#### example:
```python
functions.getData("account", "id", 'UCYdb_cMCuZGQlbajT50gpyw')
myCursorChannelRequest = functions.getDataCursor
for (channelTitle, id, priority) in myCursorChannelRequest:
	print(channelTitle)
	print(id)
	print(priority)
```

### Entry checking

#### code:
```python
functions.entryExists("id_value")
```
> return: The cursor data

#### example:
```python
entryExists = functions.getDataContentCheck(urlid)
if enteryExist:
	print("the entery exists!")
```
> note: The reason this is a seperated function is because the *getDataContentCheck* uses an other cursor then *getData*, this way it can be used within the checkloop in main.py