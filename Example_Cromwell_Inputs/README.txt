First, look at readme for Tigris: https://github.com/sema4genomics/tigris


Example Cromwell Run command to submit a job to a Valinor environment:

java -Dconfig.file=Manifests/${SAMPLE}.aws.conf -jar ~/bin/cromwell-36.jar run \
                -i ~/Rhythm/2019-02-23_WWP5/Manifests/${SAMPLE}.json \
                ~/Rhythm/2019-02-23_WWP5/RhythmGermline.wdl \
                -o ~/Rhythm/2019-02-23_WWP5/Rtm_wf_options2.json \
                > ~/Rhythm/2019-02-23_WWP5/Logs/${SAMPLE}.${TS}.log 2>&1

For Cromwell Server:
