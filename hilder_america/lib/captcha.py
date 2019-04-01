import requests
from hashlib import md5


class RClient:
    def __init__(self, username='ruokuaimiyao', password='205290mima', soft_id='95632',
                 soft_key='6b8205cf61944329a5841c30e5ed0d5d', ):
        self.username = username
        self.password = md5(password.encode()).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        return r.json()


if __name__ == '__main__':
    rc = RClient()
    im = open('test_capcha.png', 'rb').read()
    print(rc.rk_create(im, 3060))
