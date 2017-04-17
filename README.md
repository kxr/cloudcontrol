## Cloud Control

Cloud control is a simple single page dashboard type application to control the sequential startup and shutdown of application environments in AWS. It lets you manage your testing/staging environments deployed in AWS that are order sensitive i.e. they should be started/stopped in a specific order. It is currently limited to application running on EC2 only.

### Design

These are the main components:

* **Flask based backend:** The backend is written in flask with three simple views /, /instances and /envstatus. / is the main view i.e. the main dashboard. The other two views are used by bootstrap to update the information on the page. See cloudcontrol.py for more details.

* **Bootstrap based frontend:** The front end is simple bootstrap with navigation bar on top, a status window, and the instances table that shows live status of the instances. See templates/index.html for more details.

* **Python based Start/Stop script:** A basic script that is executed by flask when the start/stop operation is initiated from the dashboard. See env_start_stop.py for more details.

### Requirements

* Python >= 2.7 or 3.4 with Flask, Flask-Caching and Boto3 libraries
* AWS credentials with start,stop and describe instances privilege.
* Optionally Apache with WSGI, if you want to host the app in apache.

I've tested this application on both python 2.7.5 and 3.4.5 running on Linux. 

### Setup

* Clone: ```git clone http://github.com/kxr/cloudcontrol.git ```

* Install dependencies: ```pip install -r requirements.txt```

* Set the configuration variables in:  ```config.py```

* And start the application: ```python cloudcontrol.py```

* Browse to: ```http://hostname-or-ip:5000```

If you want to deploy this application in apache, a sample configuration is provided in file: cloudcontrol.conf.apache_example. When deploying with apache, please make sure that the apache/wsgi user has permission to create a new file in root directory of the application and write to envstatus.txt file.

## Background

I was working on moving a testing environment of a properietary application to AWS. The application was distributed on several instances each hosting some part of the application. Since this was a testing environment, the application was only started on AWS when required. The problem was that the application required a specific order in which the services should be started up or it would fail.

Lets say if the application was composed of services running on 5 instances, Instance01-05, to start up the application successfully, you would need to start Instance01 first, wait for its services to start and then start instances Instance02 and 03, wait for their services to start and finally start Instance04 and 05. If you startup all the instances at once, services on Instance02 and Instance03 would crash since they expected services on Instance01 to be up.

Admittedly, This was a bad application design problem. But fixing the application design was out of range, not to mention the application was proprietary.

Secondly, The environment start and stop ability was also required to be given to the users and/or application testers so that they can start and stop on demand. Which warranted a need for a simplistic start/stop dashboard leading to the birth of this application.

