import json
import logging
import re

import requests
import simplejson
from django.core import serializers
from requests import ReadTimeout

from api_test.common.common import record_result, check_json
from api_test.models import GlobalHost, AutomationCaseApi, AutomationHead, AutomationParameter, AutomationTestResult, \
    AutomationParameterRaw
from api_test.serializer import AutomationCaseApiSerializer, AutomationParameterRawSerializer

logger=logging.getLogger(__name__)


def test_api(host_id,case_id,project_id,_id):
    """
    执行接口测试
    :param host_id:
    :param case_id:
    :param project_id:
    :param _id:
    :return:
    """
    host=GlobalHost.objects.get(id=host_id,project=project_id)
    data=AutomationCaseApiSerializer(AutomationCaseApi.objects.get(id=_id,automation_test_case=case_id)).data

    http_type=data['http_type']
    request_type=data['request_type']
    address=host.host+data['api_address']
    head=json.loads(serializers.serialize('json',AutomationHead.objects.filter(automation_case_api=_id)))
    header={}
    request_parameter_type=data['request_parameter_type']
    examine_type=data['examine_type']
    http_code=data['http_code']
    response_parameter_list=data['response_data']
    url='http://'+address if http_type=="HTTP" else 'https://'+address

    if request_parameter_type=='form-data':
        parameter_list=json.loads(serializers.serialize('json',AutomationParameter.objects.filter(automation_case_api=_id)))
        parameter={}

        for param in parameter_list:
            key=param['fields']['name']
            value=param['fields']['value']

            try:
                if param['fields']['interrelate']:
                    # 匹配<response>[]中间的数据
                    interrelate_type = re.findall('(?<=<response>\[).*?(?=\])', value)
                    if interrelate_type[0] == "JSON":
                        api_id = re.findall('(?<=<response>\[JSON\[).*?(?=\])', value)
                        a = re.findall('(?<=\[").*?(?="])')
                        try:
                            param_data = eval(json.loads(serializers.serialize('json',
                                                                               AutomationTestResult.objects.filter(
                                                                                   automation_case_api=api_id[0])))
                                              [0]['fields']['response_data'])
                            for j in a:
                                param_data = param_data[j]
                        except Exception as e:
                            logging.exception(e)
                            record_result(_id=id, url=url, request_type=request_type, header=header, parameter=parameter,
                                          host=host.name,
                                          status_code=http_code, examine_type=examine_type,
                                          examine_data=response_parameter_list,
                                          _result='Error', code="", response_data="关联有误")
                            return "fail"
                    elif interrelate_type[0] == "Regular":
                        api_id = re.findall('(?<=<response>\[Regular\[).*?(?=\])', value)
                        patten = re.findall('(?<=\[").*?(?="])')
                        param_data = json.loads(serializers.serialize('json', AutomationTestResult.objects.filter(
                            automation_case_api=api_id[0])))
                        [-1]['fields']['response_data']
                        param_data = re.findall(patten[0], param_data.replace("\'", "\""))[0]
                    else:
                        record_result(_id=id, url=url, request_type=request_type, header=header, parameter=parameter,
                                  host=host.name,
                                  status_code=http_code, examine_type=examine_type,
                                  examine_data=response_parameter_list,
                                  _result='Error', code="", response_data="")
                        return "fail"
                    patten = re.compile(r'<response\[.*]')
                    parameter[key] = re.sub(patten, str(param_data), value)
                else:
                    parameter[key]=value
            except KeyError as e:
                logging.exception(e)
                record_result(_id=id, url=url, request_type=request_type, header=header, parameter=parameter,
                              host=host.name,
                              status_code=http_code, examine_type=examine_type,
                              examine_data=response_parameter_list,
                              _result='Error', code="", response_data="")
                return "fail"
            if data["formatRaw"]:
                request_parameter_type="raw"
    else:
        parameter=AutomationParameterRawSerializer(AutomationParameterRaw.objects.filter(automation_case_api=_id))

        if len(parameter):
            if len(parameter[0]["data"]):
                try:
                    parameter=eval(parameter[0]["data"])
                except Exception as e:
                    logging.exception(e)
                    record_result(_id=id, url=url, request_type=request_type, header=header, parameter=parameter,
                                  host=host.name,
                                  status_code=http_code, examine_type=examine_type,
                                  examine_data=response_parameter_list,
                                  _result='Error', code="", response_data="")
                    return 'fail'
            else:
                parameter={}
        else:
            parameter={}

    for i in head:
        key=i['fields']['name']
        value=i['fields']['value']
        if i['fields']['interrelate']:
            try:
                interrelate_type=re.findall('(?<=<request\[).*?(?=\])',value)
                if interrelate_type[0]=='json':
                    api_id=re.findall('(?<=<request\[JSON]\[).*?(?=\])',value)
                    a=re.findall('(?<=\[").*?(?="])',value)
                    try:
                        param_data=eval(json.loads(serializers.serialize('json',AutomationTestResult.objects.filter(automation_case_api=api_id[0])))[-1]['fields']['responseData'])
                        for j in a:
                            param_data=param_data[j]
                    except Exception as e:
                        logging.exception(e)
                        record_result(_id=id, url=url, request_type=request_type, header=header, parameter=parameter,
                                      host=host.name,
                                      status_code=http_code, examine_type=examine_type,
                                      examine_data=response_parameter_list,
                                      _result='Error', code="", response_data="")
                        return 'fail'
                elif interrelate_type[0]=="Regular":
                    api_id = re.findall('(?<=<response>\[Regular\[).*?(?=\])', value)
                    patten = re.findall('(?<=\[").*?(?="])')
                    param_data = json.loads(serializers.serialize('json', AutomationTestResult.objects.filter(
                        automation_case_api=api_id[0])))
                    [-1]['fields']['response_data']
                    param_data = re.findall(patten[0], param_data.replace("\'", "\""))[0]
                else:
                    record_result(_id=id, url=url, request_type=request_type, header=header, parameter=parameter,
                                  host=host.name,
                                  status_code=http_code, examine_type=examine_type,
                                  examine_data=response_parameter_list,
                                  _result='Error', code="", response_data="")
                    return "fail"
                patten=re.compile(r'<response\[.*]')
                header[key]=re.sub(patten,str(param_data),value)
            except Exception as e:
                logging.exception(e)
                record_result(_id=id, url=url, request_type=request_type, header=header, parameter=parameter,
                              host=host.name,
                              status_code=http_code, examine_type=examine_type,
                              examine_data=response_parameter_list,
                              _result='Error', code="", response_data="")
                return 'fail'
        else:
            header[key]=value
    try:
        if request_type=="GET":
            code,response_data,header_data=get(header,url,request_parameter_type,parameter)
        else:
            code,response_data,header_data=post(header,url,request_parameter_type,parameter)
    except ReadTimeout:
        logging.exception(ReadTimeout)
        record_result(_id=id, url=url, request_type=request_type, header=header, parameter=parameter,
                      host=host.name,
                      status_code=http_code, examine_type=examine_type,
                      examine_data=response_parameter_list,
                      _result='Timeout', code=code, response_data=response_data)
        return 'timeout'
    if examine_type=="no_check":
        record_result(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                      host=host.name,
                      status_code=http_code, examine_type=examine_type,
                      examine_data=response_parameter_list,
                      _result='PASS', code=code, response_data=response_data)
        return 'success'
    elif examine_type=='json':
        if int(http_code)==code:
            if not response_parameter_list:
                response_parameter_list='{}'
            try:
                logging.info(response_parameter_list)
                logging.info(response_data)
                result=check_json(json.loads(response_parameter_list),response_data)
            except Exception:
                logging.info(response_parameter_list)
                result=check_json(eval(response_parameter_list.replace('true','True').replace('false','False').replace('null','None')),response_data)
            if result:
                record_result(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                              host=host.name,
                              status_code=http_code, examine_type='JSON校验',
                              examine_data=response_parameter_list,
                              _result='Pass', code=code, response_data=response_data)
            else:
                record_result(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                              host=host.name,
                              status_code=http_code, examine_type='JSON校验',
                              examine_data=response_parameter_list,
                              _result='FAIL', code=code, response_data=response_data)
            return result
        else:
            record_result(_id=_id, url=url, request_type=request_type, header=header, parameter=parameter,
                          host=host.name,
                          status_code=http_code, examine_type='JSON校验',
                          examine_data=response_parameter_list,
                          _result='FAIL', code=code, response_data=response_data)
            return 'fail'


def post(header,address,request_parameter_type,data):
    """
    post 请求
    :param header:
    :param address:
    :param request_parameter_type:
    :param data:
    :return:
    """
    if request_parameter_type=="raw":
        data=json.dumps(data)
    response=requests.post(url=address,data=data,header=header,timeout=8)
    try:
        return response.status_code,response.json(),response.headers
    except json.decoder.JSONDecodeError:
        return response.status_code,'',response.headers
    except simplejson.errors.JSONDecodeError:
        return response.status_code,'',response.headers
    except Exception as e:
        logging.exception("ERROR")
        logging.error(e)
        return {},{},response.headers


def get(header,address,request_parameter_type,data):
    """
    get请求
    :param header:
    :param address:
    :param request_parameter_type:
    :param data:
    :return:
    """
    if request_parameter_type=="raw":
        data=json.dumps(data)
    response=requests.get(url=address,params=data,headers=header,timeout=8)
    if response.status_code==301:
        response=requests.get(url=response.headers["location"])
    try:
        return response.status_code,response.json(),response.headers
    except json.decoder.JSONDecodeError:
        return response.status_code,'',response.headers
    except simplejson.errors.JSONDecodeError:
        return response.status_code,'',response.headers
    except Exception as e:
        logging.exception("ERROR")
        logging.error(e)
        return {}, {}, response.headers
