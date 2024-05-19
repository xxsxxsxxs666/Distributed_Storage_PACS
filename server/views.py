
# Create your views here.
from django.http import FileResponse, JsonResponse, Http404, HttpResponse
import os
import json
from hdfs import InsecureClient
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt


def read_dicom(request, patient_id, file_index):
    # base_dir = 'H:\研究生相关\大数据\project2\django_learning\service\patientdcm'
    base_dir = '/home/master/django_project/service/patientdcm/'
    patient_dir = os.path.join(base_dir, patient_id)

    try:
        dicom_files = [f for f in os.listdir(patient_dir) if f.endswith('.dcm')]
        dicom_files.sort()
        file_name = dicom_files[file_index]
        file_path = os.path.join(patient_dir, file_name)
        file = open(file_path, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment;filename="{file_index}.dcm"'
        return response
    except IndexError:
        raise Http404("File not found")
    except FileNotFoundError:
        raise Http404("Patient not found")


def read_dicom_test(request, patient_id, file_index):
    # base_dir = 'H:\研究生相关\大数据\project2\django_learning\service\patientdcm'
    base_dir = '/home/master/django_project/service/patientdcm/'
    # /home/master/django_project/service/patientdcm/
    patient_dir = os.path.join(base_dir, patient_id)


    dicom_files = [f for f in os.listdir(patient_dir) if f.endswith('.dcm')]
    dicom_files.sort()
    file_name = dicom_files[file_index]
    file_path = os.path.join(patient_dir, file_name)
    res = {
        'success': True,
        'file_name': file_name,
        'file_path': file_path
    }

    return HttpResponse(json.dumps(res), content_type='application/json')


def get_patient_dcm_list_test(request, patient_id):
    # base_dir = 'H:\研究生相关\大数据\project2\django_learning\service\patientdcm'
    base_dir = '/home/master/django_project/service/patientdcm/'
    patient_dir = os.path.join(base_dir, patient_id)
    # calculate how many dcm file in the patient directory
    dicom_files = [f for f in os.listdir(patient_dir) if f.endswith('.dcm')]
    res = {
        'success': True,
        'file_name': base_dir,
        'file_path': patient_dir,
        'file_count': len(dicom_files)
    }

    return HttpResponse(json.dumps(res), content_type='application/json')


def get_patient_dcm_list(request, patient_id):
    # base_dir = 'H:\研究生相关\大数据\project2\django_learning\service\patientdcm'
    base_dir = '/home/master/django_project/service/patientdcm/'
    patient_dir = os.path.join(base_dir, patient_id)

    try:
        dicom_files = [f for f in os.listdir(patient_dir) if f.endswith('.dcm')]
        dicom_files.sort()
        return JsonResponse(dicom_files, safe=False)
    except FileNotFoundError:
        raise Http404("Patient not found")


from django.http import FileResponse, JsonResponse, Http404
import os
from hdfs import InsecureClient
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt

HDFS_URL = 'http://192.168.70.10:50070'  # HDFS 的 Namenode 地址
PATIENTDCM_DIR = '/user/patientdcm'  # HDFS 上存储 DICOM 文件的基目录
LOCAL_NEWPATIENTDCM_DIR = 'H:/研究生相关/大数据/project2/django_learning/service/newpatientdcm'  # 本地存储新的患者数据的目录

client = InsecureClient(HDFS_URL)


@csrf_exempt
def read_dicom_hadoop(request, patient_id, file_index):
    patient_dir = os.path.join(PATIENTDCM_DIR, patient_id).replace("\\", "/")

    try:
        dicom_files = [f for f in client.list(patient_dir) if f.endswith('.dcm')]
        dicom_files.sort()
        file_name = dicom_files[file_index]
        file_path = os.path.join(patient_dir, file_name).replace("\\", "/")

        with client.read(file_path) as reader:
            dicom_file = BytesIO(reader.read())
            dicom_file.seek(0)
            response = FileResponse(dicom_file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename="{file_index}.dcm"'
            response['Access-Control-Allow-Origin'] = '*'
            return response
    except IndexError as e:
        print(f"IndexError: {str(e)}")
        raise Http404("File not found")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {str(e)}")
        raise Http404("Patient not found")
    except Exception as e:
        print(f"Exception: {str(e)}")
        raise Http404("An error occurred")


@csrf_exempt
def get_patient_dcm_list_hadoop(request, patient_id):
    patient_dir = os.path.join(PATIENTDCM_DIR, patient_id).replace("\\", "/")

    try:
        dicom_files = [f for f in client.list(patient_dir) if f.endswith('.dcm')]
        dicom_files.sort()
        response = JsonResponse(dicom_files, safe=False)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {str(e)}")
        raise Http404("Patient not found")
    except Exception as e:
        print(f"Exception: {str(e)}")
        raise Http404("An error occurred")


@csrf_exempt
def copy_newpatient_to_patient(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        files = request.FILES.getlist('files')
        if not files:
            return JsonResponse({'status': 'failure', 'message': 'No files provided'}, status=400)

        try:
            # 确定患者目录路径
            patient_dir = os.path.join(PATIENTDCM_DIR, patient_id).replace("\\", "/")

            # 创建患者目录（如果不存在）
            if not client.status(patient_dir, strict=False):
                client.makedirs(patient_dir)

            # 写入每个上传的文件到HDFS
            for file in files:
                file_name = file.name
                dst_path = os.path.join(patient_dir, file_name).replace("\\", "/")
                with file.open('rb') as file_data:
                    client.write(dst_path, file_data.read(), overwrite=True)

            return JsonResponse({'status': 'success'}, status=200)
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {str(e)}")
            raise Http404("Patient not found")
        except Exception as e:
            print(f"Exception: {str(e)}")
            raise Http404("An error occurred")

    return JsonResponse({'status': 'failure', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_all_patients_hadoop(request):
    try:
        # 获取Hadoop文件系统中的所有患者目录
        patients = client.list(PATIENTDCM_DIR)
        patients.sort()
        response = JsonResponse(patients, safe=False)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        print(f"Exception: {str(e)}")
        raise Http404("An error occurred")


if __name__ == '__main__':
    copy_newpatient_to_patient(None)
