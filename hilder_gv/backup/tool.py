import requests
from lxml import etree
from urllib import parse


class Tool:
    @classmethod
    def get_view_state(cls, url, view_state, event_validation, post_data=None, headers=None):
        """
        传入view_state,event_validation的xpath
        :param url: http://www.jscsfc.com/NewHouse/
        :param view_state: //*[@id="__VIEWSTATE"]/@value
        :param event_validation: //*[@id="__EVENTVALIDATION"]/@value
        :return: {'__VIEWSTATE': html_tree.xpath(view_state),
                '__EVENTVALIDATION': html_tree.xpath(event_validation)}
        """
        if post_data is None:
            res = requests.get(url, headers=headers)
            html_tree = etree.HTML(res.text)
        else:
            res = requests.post(url, headers=headers, post_data=post_data)
            html_tree = etree.HTML(res.text)

        return {'__VIEWSTATE': html_tree.xpath(view_state)[0],
                '__EVENTVALIDATION': html_tree.xpath(event_validation)[0]}

    @classmethod
    def url_quote(cls, url, encode=None):
        """
        把url里面的中文转码
        :param url: str
        :param encode: default utf-8
        :return: str
        """
        url_encode = ''
        for ch in url:
            if '\u4e00' <= ch <= '\u9fff':
                ch = parse.quote(ch, encoding=encode)
            url_encode = (str(url_encode) + str(ch))
        return url_encode


if __name__ == '__main__':
    # view_dict = Tool.get_view_state('http://www.jscsfc.com/NewHouse/',
    #                                 view_state='//*[@id="__VIEWSTATE"]/@value',
    #                                 event_validation='//*[@id="__EVENTVALIDATION"]/@value')
    # print(view_dict)

    result = Tool.url_quote('www.//百度.com测试', )
    print(result)
