import boto3
import argparse


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--jobid', nargs=2 , required=False,
                        help='--jobid 34341-4343-434-5355 ecs_cluster_name   -- batch jobid to find ec2 instance running and ecs cluster name')

    args = parser.parse_args()
    if args.jobid:
        containter_ec2(args.jobid)

def containter_ec2(args):

    clientb=boto3.client('batch')
    response = clientb.describe_jobs(
        jobs=[
            args[0],
        ]
    )
    for job in response['jobs']:
        if job['jobId'] == args[0]:
            print("job status is  {:} running on {:}".format(job['status'],job['container']['containerInstanceArn']))
            container_instance_arn=job['container']['containerInstanceArn']
            break


    cliente = boto3.client('ecs')
    response = cliente.describe_container_instances(
        cluster=args[1],
        containerInstances=[
            container_instance_arn
        ]
    )
    #print (str(response['containerInstances']))
    for ent in response['containerInstances']:
        print ("jobs {:} running on instance id {:} ".format(args[0],ent['ec2InstanceId']))




if __name__ == '__main__':
    main()
