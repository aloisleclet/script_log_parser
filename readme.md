# script_log_parser

## How to use ?

1. Create alias

``` shell
echo 'alias logs="vim /path/to/logs.md"' >> ~/.zshrc
echo 'alias logtime="python3 /path/to/script_log_parser/parser.py"' >> ~/.zshrc
```

2. Log your activities


```shell
logs
```

(see ./logs_exemple.md)

3. Read your statistics

```shell
logtime --day
logtime -d
logtime --week
logtime --w
logtime --month
logtime -m
logtime --year
logtime -y

logtime --all
```
