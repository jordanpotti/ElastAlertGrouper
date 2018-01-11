# ElastAlertGrouper
A feature extension to ease the automation of Threat Hunting with ElastAlert and the ELK Stack by allowing us to perform various [Threat Hunting techniques](https://sqrrl.com/threat-hunting-reference-guide/)
 #### [@ok_bye_now](https://twitter.com/ok_bye_now)

Due to the way ELK 6.x works with indices and types, this tool may not work with versions 6.x or newer. Will be working on integrating this in the near future.

### More resources for Threat Hunting
* [Various Elastic and Threat Hunting articles](https://jordanpotti.com/tag/elastic/)
* [A ready to go ELK Stack for Threat Hunting](https://github.com/Cyb3rWard0g/HELK)
* [Setting up an ELK and Threat Hunint Lab](https://cyberwardog.blogspot.com/2017/02/setting-up-pentesting-i-mean-threat_98.html)
* [Elastic Producs](https://www.elastic.co/products)

## Why?

The arise for something like this came from the need to alert when a group of events takes place. You can determine what events you want to add and you can add as many or as few as you would like. It's easy to alert when multiple events take place but the trouble starts when we need to make sure they are all from the same host. If you figure out how to do this with native ElastAlert rules, let me know :)

Want to alert when 4 certain DLLs are accessed and a new network connection is initiated within a 3 second period? This tool can allow you to do that. ElastAlert support mentioned that this would be a feature at some point but it has not been released yet. 

This tool requires little setup, just a few nuances you need to keep in mind when setting up your rules.

## Pre-Requisites

* Created with Python 3.6

## Setup

* [I wrote a short blog post regarding the setup.](https://jordanpotti.com/2018/01/03/automating-the-detection-of-mimikatz-with-elk/)

1. Copy the py-alert.py script to /bin
2. Change the permissions on /bin/py-alert.py to make it executable. 
`sudo chmod 755 /bin/py-alert.py`
3. Create your alert rules and for alert type, use `command`
eg. 
```yaml
es_host: localhost
es_port: 9200
name: "hid"
realert:
    minutes: 0
index: winlogbeat-*
filter:
- query:
    wildcard:
        event_data.ImageLoaded: "*hid*"
type: any
alert:
    - command
command: ["/bin/py-alert.py","-T","D","-a","Mimikatz","-c","%(computer_name)s"]
```
Command Options:
```
-T: Two options here, D (Document) and S (Send). For the individual events you want to alert on, use -D (We are documenting the host)
-a: Alert Type, this is used for the body of the alert.
-c: This is the piece of identification you want to use to make sure all the alerts came from the same source device. You can change coputer_name to whatever identifying field you want.
```
4. Now that we created all of our individual rules, we need to create or master rule that calls our individual rules.
eg.
```
es_host: localhost
es_port: 9200
name: "Mimikatz"
index: elastalert_status
realert:
    minutes: 0
type: cardinality
cardinality_field: rule_name
max_cardinality: 4
filter:
- terms:
    rule_name:
        - winscard
        - cryptdll
        - hid
        - samlib
        - vaultcli
- term:
    alert_sent: true
timeframe:
    seconds: 1
alert:
    - slack
alert:
    - command
command: ["python3","/bin/py-alert.py", "-T","S","-S","SLACKWEBHOOK","-a","Mimikatz","-t","5"]
```
Command Options:
```
-T: Two options here, D (Document) and S (Send). For this alert, we want to use S because we are sending an alert.
-S: This is our Slack Web Hook. Just a URL you can generate from a Slack addon.
-a: Alert Type, this is used for the body of the alert.
-t: This is the number of individual alerts you have listed.
```
You will also need to change `max_cardinality: 4` to the number of individual alerts you have minus 1.

You may need to change what field you use for your timestamp, by default, it uses `@timestamp` which is when the alert triggered not exactly when the event happened. You can look at your timestamp options if you view your elastalert-index index in Kibana.

5. Restart you ElastAlert service.
`service elastalert restart`

6. Check for errors in starting.
`service elastalert status`




