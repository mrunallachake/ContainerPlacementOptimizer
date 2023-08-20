from google.cloud import monitoring_v3
import json
import datetime

# Set the project ID and time range for the query
project_id = "sampleproject-380205"
end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(minutes=10)

# Create a client for the Stackdriver Monitoring API
client = monitoring_v3.MetricServiceClient()

# Define the query to get CPU utilization for all VMs in the cluster
cpu_query = f'resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/cpu/utilization" AND resource.label."project_id"="{project_id}"'

# Execute the CPU query and retrieve the results
cpu_results = client.list_time_series(
    name="projects/" + project_id,
    filter=cpu_query,
    interval={"start_time": start_time, "end_time": end_time},
)

# Define the query to get RAM utilization for all VMs in the cluster
ram_query = f'resource.type="gce_instance" AND metric.type="agent.googleapis.com/memory/percent_used" AND metric.label."state"="used" AND resource.label."project_id"="{project_id}"'

# Execute the RAM query and retrieve the results
ram_results = client.list_time_series(
    name="projects/" + project_id,
    filter=ram_query,
    interval={"start_time": start_time, "end_time": end_time},
)

# Define the query to get disk utilization for all VMs in the cluster
disk_query = f'resource.type="gce_instance" AND metric.type="agent.googleapis.com/disk/percent_used" AND metric.label."state"="used" AND resource.label."project_id"="{project_id}"'

# Execute the RAM query and retrieve the results
disk_results = client.list_time_series(
    name="projects/" + project_id,
    filter=disk_query,
    interval={"start_time": start_time, "end_time": end_time},
)

# Convert the results to a list of dictionaries and save to a JSON file
data = []
temp = []
dic = {}
id_to_hostname = {}

for result in cpu_results:
    vm_hostname = result.metric.labels["instance_name"]
    vm_id = result.resource.labels["instance_id"]
    id_to_hostname[vm_id] = vm_hostname
    dic[vm_hostname] = {}

for result in cpu_results:
    temp = []
    vm_hostname = result.metric.labels["instance_name"]
    for point in result.points:
        timestamp = datetime.datetime.fromtimestamp(point.interval.start_time.timestamp())
        cpu_utilization = point.value.double_value
        temp.append(cpu_utilization)
        data.append({
            "timestamp": timestamp.isoformat(),
            "vm_hostname": vm_hostname,
            "cpu_utilization": cpu_utilization
        })
    avg_cpu_utilization = sum(temp)/len(temp)
    dic[vm_hostname]["avg_cpu_utilization"] = avg_cpu_utilization
    #print(temp)

temp = []
for result in ram_results:
    temp = []
    vm_id = result.resource.labels["instance_id"]
    vm_hostname = id_to_hostname[vm_id]
    for point in result.points:
        timestamp = datetime.datetime.fromtimestamp(point.interval.start_time.timestamp())
        ram_utilization = point.value.double_value
        temp.append(ram_utilization)
        data.append({
            "timestamp": timestamp.isoformat(),
            "vm_hostname": vm_hostname,
            "ram_utilization": ram_utilization
        })
    avg_ram_utilization = sum(temp)/len(temp)
    dic[vm_hostname]["avg_ram_utilization"] = avg_ram_utilization

# Uncomment below code to get disk utilization
# temp = []
# for result in disk_results:
#     temp = []
#     vm_id = result.resource.labels["instance_id"]
#     vm_hostname = id_to_hostname[vm_id]
#     #print(vm_hostname)
#     for point in result.points:
#         timestamp = datetime.datetime.fromtimestamp(point.interval.start_time.timestamp())
#         disk_utilization = point.value.double_value
#         temp.append(disk_utilization)
#         data.append({
#             "timestamp": timestamp.isoformat(),
#             "vm_hostname": vm_hostname,
#             "ram_utilization": disk_utilization
#         })
#     avg_disk_utilization = sum(temp)/len(temp)
#     dic[vm_hostname]["avg_disk_utilization"] = avg_disk_utilization
    
# save the utilization data in json file
with open("vm_utilization.json", "w") as f:
    json.dump(dic, f, indent=4)