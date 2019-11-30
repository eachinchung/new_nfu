from random import choice

user_agent = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/17B111 NebulaSDK/1.8.100112 Nebula WK PSDType(1) AlipayDefined(nt:4G,ws:375|748|3.0) AliApp(AP/10.1.79.6010) AlipayClient/10.1.79.6010 Alipay Language/zh-Hans Region/CN",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_1 like Mac OS X) AppleWebKit/602.2.14 (KHTML, like Gecko) Mobile/14B72c MicroMessenger/7.0.5(0x17000523) NetType/4G AlipayDefined(nt:4G,ws:375|748|3.0) AliApp(AP/10.1.79.6010) AlipayClient/10.1.79.6010 Alipay Language/zh-Hans Region/CN",
    "Mozilla/5.0 (Linux; Android 8.0.0; MI 6 Build/OPR1.170623.027; wv) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 MMWEBID/2873 MicroMessenger/7.0.4.1420(0x270004C0) NetType/4G AliApp(AP/10.1.79.6010) AlipayClient/10.1.79.6010 Alipay Language/zh-Hans Region/CN",
    "Mozilla/5.0 (Linux; Android 9; EML-AL00 Build/HUAWEIEML-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 MMWEBID/2873 MicroMessenger/7.0.4.1420(0x270004C0) Process/tools NetType/4G ABI/arm64 AliApp(AP/10.1.79.6010) AlipayClient/10.1.79.6010 Alipay Language/zh-Hans Region/CN",
    "Mozilla/5.0 (Linux; U; Android 6.0.1; zh-CN; Redmi Note 3 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.20.0.37 Mobile Safari/537.36 UCBS/3.20.0.37_191118094059 NebulaSDK/1.8.100112 Nebula AlipayDefined(nt:WIFI,ws:360|0|3.0) AliApp(AP/10.1.80.8050) AlipayClient/10.1.80.8050 Language/zh-Hans useStatusBar/true isConcaveScreen/false Region/CN",
    "Mozilla/5.0 (Linux; U; Android 9; zh-CN; MIX 2S Build/PKQ1.180729.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/11.8.8.968 UWS/2.13.2.91 Mobile Safari/537.36 UCBS/2.13.2.91_190617211143 NebulaSDK/1.8.100112 Nebula AlipayDefined(nt:WIFI,ws:393|0|2.75,ac:sp) AliApp(AP/10.1.65.6567) AlipayClient/10.1.65.6567 Language/zh-Hans useStatusBar/true isConcaveScreen/false",
    "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-CN; M6 Note Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.20.0.32 Mobile Safari/537.36 UCBS/3.20.0.32_191012190528 NebulaSDK/1.8.100112 Nebula AlipayDefined(nt:4G,ws:360|0|3.0) AliApp(AP/10.1.78.7000) AlipayClient/10.1.78.7000 Language/zh-Hans useStatusBar/true isConcaveScreen/false Region/CN"
)


def get_user_agent():
    """
    随机一个支付宝的user_agent
    :return:
    """
    return choice(user_agent)
