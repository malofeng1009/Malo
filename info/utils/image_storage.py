from qiniu import Auth, put_data

access_key = "X78oHPbfASfWQ8gzVzwDeRd2a1mKEMUefYBgKCVI"
secret_key = "kxDYcWZcJKBsRbxWkVcyfWTbvllCjOvMQ81YYFTp"
bucket_name = "py-04-yun"


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
        print(ret, info)
    except Exception as e:
        raise e

    if info.status_code != 200:
        raise Exception("上传图片失败")
    return ret["key"]


if __name__ == '__main__':
    file = input('请输入文件路径')
    with open(file, 'rb') as f:
        storage(f.read())