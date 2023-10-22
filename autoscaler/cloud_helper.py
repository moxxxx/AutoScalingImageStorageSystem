import boto3
from botocore.config import Config
from datetime import datetime, timedelta, timezone

my_config = Config(region_name="us-east-2")


def aggregate_metric(metricName, namespace, time_in_minute):
    cloudwatch = boto3.client("cloudwatch", config=my_config)
    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metricName,
        StartTime=datetime.utcnow() - timedelta(minutes=time_in_minute),
        EndTime=datetime.utcnow(),
        Period=60,  #  1-minute granularity
        Statistics=["SampleCount"],
        Unit="None",
    )
    return response["Datapoints"]


def get_one_minute_cloudwatch(namespace):
    num_miss_list = aggregate_metric("MISS", namespace, 1)
    num_hit_list = aggregate_metric("HIT", namespace, 1)
    num_hit = 0
    num_miss = 0
    if num_hit_list:
        num_hit = num_hit_list[0]["SampleCount"]
    if num_miss_list:
        num_miss = num_miss_list[0]["SampleCount"]
    return int(num_hit), int(num_miss), int(num_hit + num_miss)


def get_30_minute_cloudwatch(namespace):
    miss_list = aggregate_metric("MISS", namespace, 30)
    hit_list = aggregate_metric("HIT", namespace, 30)
    miss = cloudwatch_to_manager(miss_list, 30 + 1)
    hit = cloudwatch_to_manager(hit_list, 30 + 1)

    return miss, hit


def cloudwatch_to_manager(cloudwatch_list, minutes):
    if not cloudwatch_list:
        return [0] * minutes
    now = datetime.now(timezone.utc)
    index_list = [
        ((now - watch["Timestamp"]).seconds // 60) % 60 for watch in cloudwatch_list
    ]
    return_list = [0] * minutes
    for i in range(len(index_list)):

        return_list[index_list[i]] = int(cloudwatch_list[i]["SampleCount"])
    return return_list[1:]


get_30_minute_cloudwatch(namespace="SITE/TRAFFIC")