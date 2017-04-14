#!/usr/bin/env python3

import sys
import os
import boto3
import config
import time
from datetime import datetime

if len( sys.argv ) == 3:
	cmd = sys.argv[1]
	env = sys.argv[2]
	if cmd == 'start' and env in config.APP_DEPENDENCY_ORDER :
		if not ( os.path.isfile( config.ENV_START_LOCK ) or os.path.isfile( config.ENV_STOP_LOCK ) ) :

			# Create Lock
			with open( config.ENV_START_LOCK, 'w' ) as lock:
				lock.writelines('{}'.format( datetime.now() ))
			# Create boto3 session
			session = boto3.Session(
				aws_access_key_id = config.AWS_ACCESS_KEY_ID,
				aws_secret_access_key = config.AWS_SECRET_ACCESS_KEY,
				region_name = config.AWS_REGION
			)
			ec2 = session.resource('ec2')
	
			with open( config.ENV_STATUS_OUT, 'w' ) as envstatus:
				envstatus.writelines( '{:%Y-%m-%d %H:%M:%S} <b>Initiating {} Environment Startup</b>\n'.format( datetime.now(), env ) )
			stage_count = 0
			for stage in reversed( config.APP_DEPENDENCY_ORDER[env] ) :
				stage_count += 1
				with open( config.ENV_STATUS_OUT, 'a' ) as envstatus:
					envstatus.writelines( '{:%Y-%m-%d %H:%M:%S} <b>Startup Stage {}:</b> {} ... '.format( datetime.now(), stage_count, str(stage) ) )
				filter = [ { 'Name': 'tag:Name', 'Values': stage } ]
				filtered_instances=ec2.instances.filter(Filters=filter)
				filtered_instances.start()
				# Wait for the instances to start
				all_running = False
				while not all_running:
					time.sleep(5)
					all_running = True
					for i in filtered_instances:
						if i.state['Name'] != 'running':
							all_running = False
				with open( config.ENV_STATUS_OUT, 'a' ) as envstatus:
					envstatus.writelines( '<b>Startup Successfull ... Waiting for Services.</b>\n' )
				time.sleep(config.INTER_DEPENDENCY_START_DELAY)
			with open( config.ENV_STATUS_OUT, 'w' ) as envstatus:
				envstatus.writelines( '{:%Y-%m-%d %H:%M:%S} <b>{} Environment Started</b>'.format( datetime.now(), env ) )

			# Remove Lock
			os.remove( config.ENV_START_LOCK )
	
	elif sys.argv[1] == 'stop' and sys.argv[2] in config.APP_DEPENDENCY_ORDER :
		if not ( os.path.isfile( config.ENV_START_LOCK ) or os.path.isfile( config.ENV_STOP_LOCK ) ) :

			# Create Lock
			with open( config.ENV_STOP_LOCK, 'w' ) as lock:
				lock.writelines('{}'.format( datetime.now() ))

			# Create boto3 session
			session = boto3.Session(
				aws_access_key_id = config.AWS_ACCESS_KEY_ID,
				aws_secret_access_key = config.AWS_SECRET_ACCESS_KEY,
				region_name = config.AWS_REGION
			)
			ec2 = session.resource('ec2')

			with open( config.ENV_STATUS_OUT, 'w' ) as envstatus:
				envstatus.writelines( '{:%Y-%m-%d %H:%M:%S} <b>Initiating {} Environment Shutdown</b>\n'.format( datetime.now(), env ) )
			stage_count = 0
			for stage in config.APP_DEPENDENCY_ORDER[env] :
				stage_count += 1
				with open( config.ENV_STATUS_OUT, 'a' ) as envstatus:
					envstatus.writelines( '{:%Y-%m-%d %H:%M:%S} <b>Shutting Down Stage {}:</b> {} ... '.format( datetime.now(), stage_count, str(stage) ) )
				filter = [ { 'Name': 'tag:Name', 'Values': stage } ]
				filtered_instances=ec2.instances.filter(Filters=filter)
				filtered_instances.stop( Force=False )
				# Wait for the instances to stop
				any_running = True
				while any_running:
					time.sleep(5)
					any_running = False
					for i in filtered_instances:
						if i.state['Name'] != 'stopped':
							any_running = True
				with open( config.ENV_STATUS_OUT, 'a' ) as envstatus:
					envstatus.writelines( '<b>Shutdown Successfull</b>\n' )

			with open( config.ENV_STATUS_OUT, 'w' ) as envstatus:
				envstatus.writelines( '{:%Y-%m-%d %H:%M:%S} <b>{} Environment Stopped</b>'.format( datetime.now(), env ) )
					
			# Remove Lock
			os.remove( config.ENV_STOP_LOCK )

