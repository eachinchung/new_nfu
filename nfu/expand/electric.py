from dataclasses import dataclass
from json import decoder, loads
from re import search

from requests import session

from nfu.NFUError import NFUError


def get_electric_data(room: int) -> float:
    """
    获取宿舍电费

    :param room: 宿舍id
    :return: 一个元组，通常我规定第一个为bool，用来判定是否成功获取数据。
    :raise OSError: 一般错误为超时，学校系统炸了，与我们无关
    """

    url = 'http://axf.nfu.edu.cn/electric/getData/getReserveAM'
    data = {'roomId': room}
    http_session = session()

    try:
        response = http_session.post(url, data=data, timeout=1)
    except OSError:
        raise NFUError('安心付服务器错误')

    try:
        electric_quantity = loads(response.text)
        electric_quantity = electric_quantity['data']['remainPower']
    except (KeyError, decoder.JSONDecodeError):
        raise NFUError('此宿舍无数据')

    electric_quantity = round(float(electric_quantity), 2)
    return electric_quantity


def get_electric_create_log(room_id: int, page_index: int) -> dict:
    """
    电费充值记录
    :param room_id:
    :param page_index:
    :return:
    """
    url = 'http://axf.nfu.edu.cn/electric/order/page'
    data = {
        'ammeterId': room_id,
        'pageIndex': page_index,
        'pageSize': 10
    }
    http_session = session()

    try:
        response = http_session.post(url, data=data, timeout=1)
        electric_create = loads(response.text)['data']
    except (OSError, KeyError, decoder.JSONDecodeError):
        raise NFUError('安心付服务器错误')

    return electric_create


@dataclass
class ElectricPay:
    amount: int
    user_id: int
    name: str
    room_id: int
    building: str
    floor: str
    room: int
    __http_session = session()

    def __ready_pay(self) -> tuple:
        """
        准备支付，获取智能电表签名

        - 字段说明
            - amt 充值金额
            - custNo 学生学号
            - custName 学生姓名
            - roomId 房间号
            - areaName 学校名字，写死南方学院就行
            - architectureName 宿舍楼
            - floorName 楼层
            - roomName 楼号

        :return: 一个元组，通常我规定第一个为bool，用来判定是否成功获取数据。
        :raises OSError: 安心付晚上11点过后，无法充值电费，会报错。
        """

        url = 'http://axf.nfu.edu.cn/electric/pay/doPay'
        data = {
            'amt': self.amount,
            'custNo': self.user_id,
            'custName': self.name,
            'roomId': self.room_id,
            'areaName': '南方学院',
            'architectureName': self.building,
            'floorName': self.floor,
            'roomName': self.room
        }

        try:
            response = self.__http_session.post(url, data=data, timeout=1)
        except OSError:
            raise NFUError('与安心付服务器连接超时，请稍后再试')

        try:
            # 尝试获取签名
            json_data = search(r'name="json" value=.+', response.text).group()[19:-4]
            signature = search(r'name="signature" value=.+', response.text).group()[24:-4]
        except AttributeError:
            raise NFUError('与安心付服务器连接超时，请稍后再试')

        return json_data, signature

    def __set_wechat_pay(self, json_data, signature):
        """
        设置支付方式为微信支付

        返回 json、signature 为向支付页面 post 的 body
        只要设置好创建订单数据的 cookie，并重定向回安心付支付接口，即可调用安心付支付接口
        学校安心付接口为 post 提交，但后端并无验证，故 body 数据在 url 带上并重定向即可

        - 字段说明
            - json json_data
            - signature signature
            - payChannel 设置为微信支付

        :param json_data: ready_pay 返回的订单数据
        :param signature: ready_pay 返回的数字签名
        :return: 0.bool 1.json 2.signature 3.cookies
        :raise: OSError: 安心付晚上11点过后，无法充值电费，会报错。
        """

        url = 'http://nfu.zhihuianxin.net/paycenter/gateway_web'
        data = {
            'json': json_data,
            'signature': signature
        }
        header = {'Referer': 'http://axf.nfu.edu.cn/electric/pay/doPay'}

        try:
            # 向安心付接口 post 订单数据，无需返回值
            self.__http_session.post(url, data=data, headers=header)
        except OSError:
            raise NFUError('与安心付服务器连接超时，请稍后再试')

        url = 'http://nfu.zhihuianxin.net/paycenter/payGateway_web'
        data = {'payChannel': 'WxPay'}
        header = {'Referer': 'http://nfu.zhihuianxin.net/paycenter/gateway_web'}

        try:
            response = self.__http_session.post(url, data=data, headers=header)
        except OSError:
            raise NFUError('与安心付服务器连接超时，请稍后再试')

        try:
            json_data = search(r'name="json" value=.+', response.text).group()[19:-5]
            signature = search(r'name="signature" value=.+', response.text).group()[24:-5]
        except AttributeError:
            raise NFUError('与安心付服务器连接超时，请稍后再试')

        return json_data, signature, self.__http_session.cookies.get_dict()['JSESSIONID']

    def create_order(self):
        ready_pay = self.__ready_pay()
        return self.__set_wechat_pay(ready_pay[0], ready_pay[1])
