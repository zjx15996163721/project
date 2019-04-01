from lib.mongo import Mongo
from .qiniu_fetch import qiniufetch
import re
import yaml
from lib.log import LogHandler

setting = yaml.load(open('config_local.yaml'))

log = LogHandler("img_replace")

class ImageReplace:
    def image_download(self,article):
        if re.findall('data-src="(.*?)"',article):
            image_url_list = re.findall('data-src="(.*?)"',article)
            if len(image_url_list) == 0:
                log.info('无图片可更换！')
                return article
            else:
                new_body = re.sub('data-src="(.*?)"', self.replace, article)
                return new_body
        else:
            image_url_list = re.findall('src="(.*?)"',article)
            if len(image_url_list) == 0:
                log.info('无图片可更换！')
                return article
            else:
                new_body = re.sub('src="(.*?)"',self.replace,article)
                return new_body

    @staticmethod
    def replace(matchobj):
        file_name = matchobj.group(1)

        image_new_url = qiniufetch(file_name, file_name)
        rep = 'src="' + image_new_url + '"'
        if image_new_url is False:
            rep = '图片替换失败！'
        return rep


