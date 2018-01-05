# -*- coding: utf-8 -*-
import os
import sys
import teslajson
import boto3
import json

def handler(event, context):
    if 'source' in event and event['source'] == 'aws.events':
        return periodic()
    print event
    print "---"
    print context
    print "Nothing to do"

def periodic():
    expected_variables = ['TESLA_USERNAME', 'TESLA_PASSWORD', 'THING_BATTERY', 'THING_CLIMATE', 'THING_DRIVE']

    for expected_variable in expected_variables:
        if not expected_variable in os.environ:
            print 'Missing environment variable "%s"' % expected_variable
            sys.exit(1)

    if not 'AWS_DEFAULT_REGION' in os.environ:
        os.environ['AWS_DEFAULT_REGION'] = 'eu-central-1'

    # IoT client
    client = boto3.client('iot-data')

    print 'Connecting to Tesla...'
    c = teslajson.Connection(os.environ['TESLA_USERNAME'], os.environ['TESLA_PASSWORD'])
    v = c.vehicles[0]

    # charge state
    d = v.data_request('charge_state')
    print 'Battery level: %d' % d['battery_level']

    print 'Publishing charge state to IoT...'
    data = {
        'state' : {
            'reported' : {
              'level' : d['battery_level'],
              'state' : d['charging_state'].lower(),
              'time_to_full_charge' : d['time_to_full_charge'],
              'battery_heater_on' : d['battery_heater_on']
            }
        }
    }
    publish_iot(client, os.environ['THING_BATTERY'], data)

    # climate
    d = v.data_request('climate_state')
    print 'Temperature inside is: %d' % d['inside_temp']

    print 'Publishing climate state to IoT...'
    data = {
        'state' : {
            'reported' : {
              'temperature' : d['inside_temp'],
              'inside_temp' : d['inside_temp'],
              'outside_temp' : d['outside_temp']
            }
        }
    }
    publish_iot(client, os.environ['THING_CLIMATE'], data)

    # drive state 
    d = v.data_request('drive_state')
    if not d['speed']:
        d['speed'] = 0
    print 'Driving speed is: %d' % d['speed']

    print 'Publishing drive state to IoT...'
    data = {
        'state' : {
            'reported' : {
              'speed' : d['speed'],
              'latitude' : d['latitude'],
              'longitude' : d['longitude'],
              'heading' : d['heading'],
              'gps_as_of' : d['gps_as_of']
            }
        }
    }
    publish_iot(client, os.environ['THING_DRIVE'], data)

    return

def publish_iot(client, name, data):
    response = client.publish(
        topic='$aws/things/%s/shadow/update' % name,
        qos=1,
        payload=json.dumps(data)
    )
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print 'Error publishing to thing'
        print response
        sys.exit(1)
