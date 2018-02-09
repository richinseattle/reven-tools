from reven_api import *
import reven
import os, sys, time

'''
Reven Trace Recorder
@richinseattle

This script will create and record a scenario in reven and then generate a trace

Example:
$ python reven_trace_recorder.py 
Reven Trace Recorder

Connecting to reven server at 192.168.4.2:8080
Connected as user: trng1

Creating project: trace_createprocess.exe_1518174466.17

Uploading target binary: trace_createprocess.exe

Creating scenario configuration:
     target vm: tr1_win7_32b
  command line: trace_createprocess.exe whoami.exe

Recording scenario for project trace_createprocess.exe_1518174466.17
. . . . . . . . . . . . done

Initializing trace recording over scenario..
. . .
Trace is recording on the server.
This will take a while. Exiting..

'''

print "Reven Trace Recorder"
print


# default = "localhost"
reven_server = os.getenv('REVEN_SERVER') 
if reven_server == None:
    reven_server = "127.0.0.1"

# default = "8080"
reven_port = os.getenv('REVEN_PORT') 
if reven_port == None:
    reven_port = 8080

# default = "reven"
reven_user = os.getenv('REVEN_USER') 
if reven_user == None:
    reven_user = "reven"

# If not specified, this will create an interactive scenario 
# and will not automatically record a trace
reven_target_binary = os.getenv('REVEN_TARGET_BINARY')
if reven_target_binary == None:
    reven_target_binary = ""

# default = ""
reven_target_binary_args = os.getenv('REVEN_TARGET_BINARY_ARGS')
if reven_target_binary_args == None:
    reven_target_binary_args = ""

# default = target_binary_[timestamp]
reven_project_name = os.getenv('REVEN_PROJECT')
if reven_project_name == None:
    if reven_target_binary == "":
        reven_project_name = "%s_%s" % ("INTERACTIVE", str(time.time()))
    else:
        reven_project_name = "%s_%s" % (reven_target_binary, str(time.time()))

# default = first vm configured in reven server 
reven_project_vm = os.getenv('REVEN_PROJECT_VM')


print "Connecting to reven server at %s:%s" % (reven_server, reven_port)
try:
    reven_connection = launcher_connection(reven_server, reven_port)
except: 
    print "ERROR: could not connect to reven server. Exiting.."
    sys.exit(1)

if reven_user not in reven_connection.list_users():
    print "ERROR: supplied user name is not configured on the server. Exiting.."
    sys.exit(1)



project_id = project_id(reven_user, reven_project_name)
print "Connected as user: %s" % (reven_user)
print
print "Creating project: %s" % (reven_project_name)
print
reven_connection.project_create(project_id)

if reven_project_vm == None:
    reven_project_vm = reven_connection.list_vms()[0].name

rec_launch_conf = scenario_recording_launch_config()
rec_launch_conf.vnc_port = ""
rec_launch_conf.vnc_password =  ""
rec_launch_conf.is_interactive = False

if reven_target_binary == "":
    rec_launch_conf.is_interactive = True
else:
    print "Uploading target binary: %s" % (reven_target_binary)
    print
    reven_connection.project_upload_file(project_id, reven_target_binary)


print "Creating scenario configuration:"
print "     target vm: %s" % reven_project_vm
if reven_target_binary:
    print "  command line: %s %s" % (reven_target_binary, reven_target_binary_args)
    print
else:
    print"    WARNING: no target binary selected, creating interactive scenario and exiting.."
    sys.exit(0)

scenario_conf = scenario_config()
scenario_conf.binary_dump_hint = ""
scenario_conf.system_pdb_path = ""
scenario_conf.binary_name = reven_target_binary 
scenario_conf.vm_config_name = reven_project_vm
scenario_conf.binary_arguments = reven_target_binary_args
scenario_conf.binary_dump_address = ""

recording_conf = scenario_recording_config()
recording_conf.recording = rec_launch_conf
recording_conf.scenario = scenario_conf

print "Recording scenario for project %s\n." % (reven_project_name),
sys.stdout.flush()
reven_connection.project_record_scenario(project_id, recording_conf)

# wait for scenario to finish recording
while True:
    print ".",
    sys.stdout.flush()
    time.sleep(1)
    scen_rec_info = reven_connection.project_scenario(project_id)
    if not scen_rec_info.is_recording:
        break

print "done"
print

reven_launch_conf = reven_launch_config()
reven_launch_conf.reven_arguments = ""
reven_launch_conf.is_mono = False
reven_launch_conf.port = 1234

print "Initializing trace recording over scenario.."
project_port = reven_connection.server_launch(project_id, reven_launch_conf)
timeout = 30
for i in range(0, timeout):
    time.sleep(1)
    try:
        reven_project = reven.Project(reven_server, project_port)
        break
    except:
        print ".",
        sys.stdout.flush()

try:
    reven_project.start_execution()
 
    print
    print "Trace is recording on the server."
    print "This will take a while. Exiting.."
    print
except:
    print "ERROR: could not launch trace recording, check license status"

sys.exit(0)


