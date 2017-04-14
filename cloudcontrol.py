from flask import Flask, render_template, jsonify, request
from flask_caching import Cache
from subprocess import Popen
import os
import boto3
import config

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

#
# The Home Page
#
# This function simply passes on the appropriate data
# in the form of a dicionary, to index.html jinja2 template
#
@app.route('/', methods=['GET', 'POST'])
def index():

	# The data dictionary that will
	# be passed to the jinja2 template
	render_data={}

	# Pass on the configurations that are needed by the template
	render_data['dep_order'] = config.APP_DEPENDENCY_ORDER
	render_data['data_refresh'] = config.DATA_REFRESH
	render_data['banner'] = config.BANNER
	
	# If some thing was posted,
	if request.method == 'POST':
		# First of all make sure there are no locks
		# Add the alert in the render_data if a lock is there
		if os.path.isfile( config.ENV_START_LOCK ):
			render_data['alert'] = 'Please wait, the environment is currently booting up'
		elif os.path.isfile( config.ENV_STOP_LOCK ):
			render_data['alert'] = 'Please wait, the environment is currently shutting down'
		else:
			# If startenv was posted,
			# Call the script with start argument
			# And pass the success notification in render_data
			if 'startenv' in request.form and 'env' in request.form:
				Popen( [ 'nohup', config.ENV_START_STOP, 'start', request.form['env'] ],
					preexec_fn=os.setpgrp )
				render_data['info'] = 'Starting the environment: ' + request.form['env']
			# If stopenv was posted
			# Call the script with stop argument
			# And pass the success notification in render_data
			elif 'stopenv' in request.form and 'env' in request.form:
				Popen( [ 'nohup', config.ENV_START_STOP, 'stop', request.form['env'] ],
					preexec_fn=os.setpgrp )
				render_data['info'] = 'Stoping the environment: '  + request.form['env']
			# Some thing unknow was posted,
			# Pass the Invalid Request alert in render_data
			else:
				render_data['alert'] = 'Invalid Request'

	# Pass render_data to the jinja2 template
	return render_template('index.html', data=render_data)

#
# The Instances View
#
# We will cache the result of this view for 5 seconds
# This function will be called directly and frequently 
# by bootstrap-tables hence caching it is crucial.
# The volumes function inside this view is cached for
# even greater time, as the volume info rarely changes
# and is very time consuming to calculate on each call
#
@app.route("/instances", methods=['GET'])
@cache.cached( timeout = config.INSTANCES_CACHE )
def instances():
	# ec2 service resource
	ec2_res = boto3.Session(
		aws_access_key_id = config.AWS_ACCESS_KEY_ID,
		aws_secret_access_key = config.AWS_SECRET_ACCESS_KEY,
		region_name = config.AWS_REGION
	).resource( 'ec2' )
	# filter the instances
	ec2 = ec2_res.instances.filter( Filters=config.INSTANCE_FILTER )

	# volumes is a separate funtion that will return the ebs
	# volumes attached to each instance.
	# This was made a separate function so it can be cached separately
	@cache.cached( timeout = config.VOLUMES_CACHE, key_prefix='volumes')
	def volumes():
		return { i.id : [ str(ec2_res.Volume( id=bdm['Ebs']['VolumeId']).size)+'GB ' for bdm in i.block_device_mappings ]  for i in ec2.all() }
	vols = volumes()

	# We iterate over all the instances and collect the data
	# in instances array and finally output it in json
	instances = []	
	for i in ec2.all():
		iid = i.id
		istate = i.state['Name']
		itype = i.instance_type
		iaz = i.placement['AvailabilityZone']
		iname = ( [ it['Value'] for it in i.tags if it['Key'] == 'Name' ] or [''] )[0]
		ienv = ( [ it['Value'] for it in i.tags if it['Key'] == 'Env' ] or [''] )[0]
		ipvip = i.private_ip_address
		ivols = vols[ iid ]
		instances.append ( { 'name': iname, 'id': iid, 'az': iaz, 'env': ienv, 'type': itype, 'vols': ivols, 'privip': ipvip, 'state': istate } )
	return jsonify(instances)

#
# The Environment Status view
#
# This view will simply return the content of the status file
# present in the application root. This status file is suppose
# be updated by the script that starts/stops the environment.
# Bootstrap will call this view frequently to show the status on the homepage
#
@app.route("/envstatus", methods=['GET'])
def envstatus():
	content = ''
	with open(config.ENV_STATUS_OUT, "r+") as f:
		#for line in f:
		#	content += line
		#	content += ('<br />')
		content = f.read().replace( '\n', '<br />' )
	return(content)

if __name__ == "__main__":
	app.run()
