import os.path

APP_ROOT = os.path.dirname( os.path.abspath(__file__)  )

#####################
#                   #
# AWS Configuraiton #
#                   #
#####################

# AWS Credentials
AWS_REGION = 'eu-west-1'
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

# INSTANCE_FILTER
#
# This filter is only applied to the instances that are being displayed on the front page.
# i.e. It doesn't affect what instances are started up and stopped. The start/stop script 
# only reads the instances from INSTANCES_DEPENDENCY_ORDER.
# The value of this variable is directly passed to the filter function when calling the 
# boto3 api. Please see the "filter" section in boto3/EC2/ServiceResource docs for more details:
# http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.ServiceResource.instances
#
# For example: INSTANCE_FILTER = [ { 'Name': 'tag:Env', 'Values': ['test'] } ]
# Will only show instances that have tag Env set to value test.
# Setting it to an empyt array [] should display all instances.
INSTANCE_FILTER = []

# APP_DEPENDENCY_ORDER
# 
# This is a dictionary of all the environments/applications you want to manage with this dashboard.
# The key of each dictionary defines any arbitrary name you want to give to the environment,
# and the value of each key is a list of list instances by name i.e: EC2 Name Tag.
# The instances will be shutdown from top to bottom and started from bottom to up.
#
# For example, suppose you have two environments/applications deployed on AWS.
# APP01 env consist of four instances: ad, sqlsvr, filesvr and app.
# APP02 env consist of three instances: nfs, oradb, cms.
# And both of the environments are order sensitive, i.e you want to start/stop them up in specific order.
# APP01 requires the ActiveDirectory instance (ad) to startup first, Next then SQL and File Server and
# finally the application instance.
# APP02 requires that the nfs servers starts up first, Oracle DB server and  CMS at the end.
# In this case, you will define you environments like this:
#
# APP_DEPENDENCY_ORDER = {
# 				'APP01' : [
# 						[ 'app' ],
# 						[ 'sqlsvr', 'filesvr' ],
# 						[ 'ad' ]
# 				],
#
# 				'APP02' : [
# 						[ 'cms', 'oradb' ],
# 						[ 'nfs' ]
# 				]
# }
# This will show you two applications environment in the application dashboard to start/stop.
# When you start APP01, it will first start ad instance, wait for it to start up and once its started,
# it will start sqlsvr and filesvr instances in parallel, and wait for both of them to start,
# and finally it will start the app instance
#
# If your application environment(s) is not start-order sensitive,
# you just need to have a single array per application:
#
# APP_DEPENDENCY_ORDER = {
# 				'APP01' : [
# 						[ 'app', 'sqlsvr', 'filesvr', 'ad' ]
# 				],
#
# 				'APP02' : [
# 						[ 'cms', 'oradb', [ 'nfs' ]
# 				]
# }
APP_DEPENDENCY_ORDER = {
				'APP01' : [
						[ 'app' ],
						[ 'sqlsvr', 'filesvr' ],
						[ 'ad' ]
				],

				'APP02' : [
						[ 'cms', 'oradb' ],
						[ 'nfs' ]
				]
}

# INTER_DEPENDENCY_START_DELAY
#
# Delay in seconds after an array of instances has been started, and next array of instance(s) are started. 
# This delay can be used to wait for the services on the started instances to come up.
# Value is in seconds
INTER_DEPENDENCY_START_DELAY = 60 

#############################
#                           #
# Application Configuration #
#                           #
#############################

# BANNER
#
# Application banner, used in the title and the navbarof the front page
BANNER = "Cloud Control"

# DATA_REFRESH
#
# How frequent the data on the main page should be refreshed, it will be used in the
# javascript/ajax refresh timeout.It is not recommended to have this value less than 5 seconds
# Value is in seconds
DATA_REFRESH = 5

# INSTANCES_CACHE
#
# How long the instances data (/instances) should be cached by flask. This value is used by the flask-cache.
# It is not recommended to have this value less than 5 seconds.
# Value is in seconds
INSTANCES_CACHE = 5

# VOLUMES_CACHE
# 
# This defines, how long should the ebs volumes data be cached by flask.
# Finding EBS Volumes attached to each instance is a time consusiming operation and doesn't need to be
# updated every time we udpate the dashboard so they are cached for a extended period of time,
# Value is in seconds
VOLUMES_CACHE = 3600

# ENV_START_STOP
#
# The Start/Stop script that is execute behind the scenes, when the shutdown or startup
# operation is initiated from the dashboard.
# Having this part as a separate/autonmous script has several advantages,
# First the front end part remains simple, second this script can now be invoked
# with out the dashboard from the command line or as a cron job.
#
# There is a functional script included that will do the job for you, but feel free to
# replace it with your own script. The scripts expects two arguments,
# First argument should be either "start" or "stop". The second argument should be one of the
# application enviroments defined in APP_DEPENDENCY_ORDER above. For e.g: "APP01" or "APP02"
ENV_START_STOP = os.path.join( APP_ROOT, 'env_start_stop.py' )

# ENV_STATUS_OUT
#
# The script executed by the ENV_START_STOP will write appropriate status messages to this file,
# which will be displayed on the dashboard page.
ENV_STATUS_OUT = os.path.join( APP_ROOT, 'envstatus.txt' )


# ENV_START_LOCK, ENV_STOP_LOCK
#
# These lock files are used by the dashboard application and the ENV_START_STOP scritp,
# to create a lock while the start or stop operation is running.
ENV_START_LOCK = os.path.join( APP_ROOT, 'envstart.lock' )
ENV_STOP_LOCK = os.path.join( APP_ROOT, 'envstop.lock' )

