# tesla-aws-iot
This small Python Lambda script polls your Tesla car (via Tesla web api), get some metrics and update corresponding AWS IoT.

This means that you'll have a shadow Thing in AWS that reflect battery status, temperature, cordinations and other statuses.

This script uses three Things:

Battery - will keep status of level, charge state, etc.

Temperature - will keep status of inside, outside temperature.

Drive - will keep status of speed, location, etc.


Update _config.yaml_ with you correct credentials.

To set up your working environment:

```pip install -r requirements.txt```

To deplopy:
```lambda deploy```

To run locally:
```lambda invoke -v```

You must first create a role that lambda will run. Its a mess trying to get correct IAM policies, but you should at least allow lambda execute and iot:Publish. You also need AWS credential keys, these are used when deploying. They need to be allowed to deploy lambda functions.

Before anything can be updated, create Things. The name of each thing must be the same as the environment variables defined in _config.yaml_.

```aws iot create-thing --thing-name Tesla-temperature
aws iot create-thing --thing-name Tesla-battery
aws iot create-thing --thing-name Tesla-drive
```

Optionalily, you can accosiate a certificate with the things:

```aws iot list-certificates
aws iot attach-thing-principal --thing-name Tesla-temperatur --principal <arn>
```

Finaly, configure CloudWatch to run the function periodically.

CloudWatch Event -> Rules -> Create rule
Choose 'schedule' and then 'Fixed rate of 5 minutes'. Click 'Add Target' and specify your lambda function.
