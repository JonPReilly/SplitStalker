import os
from django_cron import CronJobBase, Schedule
from settings import BASE_DIR, LOG_OBJECT
import subprocess
import sys


import logging


class MeetPingException(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return (self.value)

class MeetPing(CronJobBase):
	"""
	Cron job that runs meetPing.py every MEETPING_CRONTASK minutes.

	On failure of meetPing.py, we need to catch the subprocess's exception/error and raise our own for 
	django_cron to process an error has occured and dump the traceback to an object in the database.
	"""
	RUN_EVERY_MINS = 1
	schedule = Schedule(run_every_mins = RUN_EVERY_MINS)

	code = 'MeetPing'

	def do(self):
		print "[MeetPingCron] Launching MeetPing..."
		log = logging.getLogger(LOG_OBJECT)
		log.info("[MeetPingCron] Launching MeetPing...")
		meetPing_script = os.path.join(BASE_DIR, "meetPing_lowbandwidth.py")
   		
		try: 
	   		rc = subprocess.check_output([sys.executable, meetPing_script] , stderr=subprocess.STDOUT )
	   	except subprocess.CalledProcessError as exc:  
	   		log.error("[MeetPingCron] Error in MeetPing. Check logs")
	   		print "[MeetPingCron] Error in MeetPing. Check logs"
	   		exeption = "RC: " + str(exc.returncode) + "\n---Output---\n"+ str(exc.output) + "\n----\n"
	   		raise MeetPingException(exeption)
	   		
	   	else:
	   		print "[MeetPingCron] MeetPing ended succesfully"
	   		log.info("[MeetPingCron] MeetPing ended succesfully")
		
