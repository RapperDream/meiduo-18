from django.conf import settings
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.utils.deconstruct import deconstructible


# 重写django默认储存类cd
@deconstructible()
class FastDFSStorage(Storage):

    def __init__(self, config=None, base_url=None):

        if config is None:
            config = settings.CONFIG

        if base_url is None:
            base_url = settings.BASE_URL

        self.client_config = config

        self.base_url = base_url

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):

        # 保存图片文件
        # 建立fastdfs连接对象  # 连接七牛云
        client = Fdfs_client(self.client_config)
        # 上传文件
        ret = client.upload_by_buffer(content.read())
        # 判断上传状态
        if ret['Status'] != 'Upload successed.':
            raise Exception('errors')

        file_id = ret['Remote file_id']

        return file_id

    def url(self, name):

        return self.base_url + name

    def exists(self, name):

        return False
