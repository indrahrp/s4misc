Example Cromwell Run command to submit a job to a Valinor environment:

java -Dconfig.file=Manifests/${SAMPLE}.aws.conf -jar ~/bin/cromwell-36.jar run \
                -i ~/Rhythm/2019-02-23_WWP5/Manifests/${SAMPLE}.json \
                ~/Rhythm/2019-02-23_WWP5/RhythmGermline.wdl \
                -o ~/Rhythm/2019-02-23_WWP5/Rtm_wf_options2.json \
                > ~/Rhythm/2019-02-23_WWP5/Logs/${SAMPLE}.${TS}.log 2>&1

For Cromwell Server:

curl -H "accept: application/json" \
-F "workflowSource=@/home/ec2-user/MAIN.wdl" \
-F "workflowInputs=@/home/ec2-user/SAMPLE.json" \
-F "workflowOptions=@/home/ec2-user/WORKFLOW_OPTIONS.json" \
-F "workflowDependencies=@WDL_DEPENDENCIES.zip" -X POST "http://<EC2_IP>/api/workflows/v1"
