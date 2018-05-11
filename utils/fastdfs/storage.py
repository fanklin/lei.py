from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client


class FdfsStorage(FileSystemStorage):
    """自定义文件存储: 通过管理后台上传文件时, 把文件上传到Fdsf"""

    def _save(self, name, content):
        """
        通过管理后台上传文件时, 会执行此方法保存上传的文件
        :param name: name 上传文件的名称
        :param content: 上传文件内容, ImageFieldFile类型, 从此对象中可以取出上传的文件内容
        :return:
        """
        # 保存上传的文件到django网站所在的服务器
        # path = super()._save(name, content)
        # info = '%s, %s, %s ' % (name, type(content), path)
        # print(info)

        # 保存文件到Fastdfs服务器
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 通过管理后台上传的文件内容
        body = content.read()
        # 上传文件到Fdfs服务器
        # {'Remote file_id': 'group1/M00/00/00/wKjSsVq7ES2AaWOlAAAAG9FSUMk2069290',
        #  'Status': 'Upload successed.'..}
        my_dict = client.upload_by_buffer(body)
        if my_dict.get('Status') == 'Upload successed.':
            # 文件上传成功
            path = my_dict.get('Remote file_id')
        else:
            print('上传文件出错')

        # path: 保存到数据库表中的文件路径
        return path

    def url(self, name):
        # nginx服务器的主机端口
        host = 'http://127.0.0.1:8888/'
        return host + super().url(name)























