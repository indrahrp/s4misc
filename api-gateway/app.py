from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as api,
    aws_certificatemanager as acm

)


class VoncVAPIStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        api_name='voncv'
        cert_arn='arn:aws:acm:us-east-1:921279086507:certificate/1cdc5fa6-0978-4c3c-96fa-ced4188b4fd0'
        # Example automatically generated. See https://github.com/aws/jsii/issues/826
        cert = acm.Certificate.from_certificate_arn(self,"cert",cert_arn)
        domain_name='voncv.sema4.com'
        domain_obj=api.DomainNameOptions(certificate=cert, domain_name=domain_name)
        #domain_name_obj=api.DefaultDomainMappingOptions( domain_name=domain_obj1, mapping_key=None)
        integration_uri='http://voncwesprod.sema4.com:3000'


        #classaws_cdk.aws_apigateway.HttpIntegration(url, *, http_method=None, options=None, proxy=None)

        #base_api=api.HttpApi(self, 'rootapi', api_name=api_name, cors_preflight=None, create_default_stage=None, default_domain_mapping=domain_name_obj)
        #                     , default_integration=None)


        base_api = api.RestApi(self, "RestApi",rest_api_name=api_name,domain_name=domain_obj,
                           deploy=False
                           )


        integration_response_200=api.IntegrationResponse(status_code='200')
        integration_response_400=api.IntegrationResponse(status_code='400',selection_pattern='400')
        integration_response_401=api.IntegrationResponse(status_code='401',selection_pattern='401')
        integration_response_404=api.IntegrationResponse(status_code='400',selection_pattern='404')
        integration_response_405=api.IntegrationResponse(status_code='401',selection_pattern='405')
        integration_response_500=api.IntegrationResponse(status_code='401',selection_pattern='500')

        integration_response_all=[integration_response_200,
                                  integration_response_400,
                                  integration_response_401,
                                  integration_response_404,
                                  integration_response_405,
                                  integration_response_500
                                  ]
        integration_options=api.IntegrationOptions(integration_responses=integration_response_all)
        #method_reponse=api.IntegrationOptions(integration_responses=integration_response_all)
        mr=[
            api.MethodResponse(status_code='200'),
            api.MethodResponse(status_code='400'),
            api.MethodResponse(status_code='401'),
            api.MethodResponse(status_code='404'),
            api.MethodResponse(status_code='405'),
            api.MethodResponse(status_code='500')
                      ]







        integration=api.Integration(type=api.IntegrationType.HTTP,integration_http_method='POST',uri=integration_uri,options=integration_options)



        control = base_api.root.add_resource('control')
        control_get=control.add_method('POST',integration)
        control_controlid=control.add_resource('{controlid}')
        control_controlid_post=control_controlid.add_method('POST',integration)
        control_controlid_sample=control_controlid.add_resource('sample')
        control_controlid_sample_sampleid=control_controlid_sample.add_resource('sampleid')
        control_controlid_sample_sampleid_get=control_controlid_sample_sampleid.add_method('GET',integration,method_responses=mr)
        control_controlid_sample_sampleid_pipelineoutput=control_controlid_sample_sampleid.add_resource('pipeline_output')
        control_controlid_sample_sampleid_pipelineoutput_post=control_controlid_sample_sampleid_pipelineoutput.add_method('POST',integration)


        getalllpatients = base_api.root.add_resource('getallpatients')
        getalllpatients_get=getalllpatients.add_method('GET',integration)


        patient = base_api.root.add_resource('patient')
        patient_post = patient.add_method('GET',integration)
        patient_get = patient.add_method('POST',integration)

        patientid=patient.add_resource('patientid')
        patient_put=patientid.add_method('PUT',integration)
        patient_get=patientid.add_method('GET',integration)

        patient_case=patientid.add_resource('case')
        patient_case_post=patient_case.add_method('POST',integration)

        patient_case_caseid=patient_case.add_resource('caseid')
        patient_case_caseid_get= patient_case_caseid.add_method('GET',integration)
        patient_case_caseid_put= patient_case_caseid.add_method('PUT',integration)
        patient_case_caseid_close=patient_case_caseid.add_resource('close')
        patient_case_caseid_close_post=patient_case_caseid_close.add_method('PUT',integration)
        patient_case_caseid_curate=patient_case_caseid.add_resource('curate')
        patient_case_caseid_curate_post=patient_case_caseid_curate.add_method('POST',integration)
        patient_case_caseid_fail=patient_case_caseid.add_resource('fail')
        patient_case_caseid_fail_post=patient_case_caseid_fail.add_method('POST',integration)
        patient_case_caseid_reopen=patient_case_caseid.add_resource('reopen')
        patient_case_caseid_reopen_post=patient_case_caseid_reopen.add_method('POST',integration)
        patient_case_caseid_sample=patient_case_caseid.add_resource('sample')
        patient_case_caseid_sample_sampleid=patient_case_caseid_sample.add_resource('sampleid')
        patient_case_caseid_sample_sampleid_get=patient_case_caseid_sample_sampleid.add_method('GET',integration)
        patient_case_caseid_sample_sampleid_fail=patient_case_caseid_sample_sampleid.add_resource('fail')
        patient_case_caseid_sample_sampleid_fail_post=patient_case_caseid_sample_sampleid_fail.add_method('POST',integration)
        patient_case_caseid_sample_sampleid_pipelineoutput=patient_case_caseid_sample_sampleid.add_resource('pipeline-output')
        patient_case_caseid_sample_sampleid_pipelineoutput_post=patient_case_caseid_sample_sampleid_pipelineoutput.add_method('POST',integration)
        patient_case_caseid_variant=patient_case_caseid.add_resource('variant')
        patient_case_caseid_variant_post=patient_case_caseid.add_method('POST',integration)
















'''
        getalllpatients.add_method('GET', example_entity_lambda_integration,
                method_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': True,
                }
            }
        ]`
        '''



app = core.App()
VoncVAPIStack(app, "VoncVStack", env={'region': 'us-east-1','account':'417302553802'})
app.synth()