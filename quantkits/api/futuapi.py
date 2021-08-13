# -*- coding: utf-8 -*-
# @Time    : 5/2/2021 9:27 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: futuapi.py
# @Software: PyCharm
import os
import time
from time import sleep
from datetime import time as timer
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from typing import List, Union
from futu import (
    OpenQuoteContext,
    SubType,
    KLType,
    AuType,
    SecurityType,
    RET_ERROR,
    RET_OK,
    BrokerHandlerBase,
    CurKlineHandlerBase,
    KL_FIELD,
    Market,
    Plate,
    SortField,
    SimpleFilter,
    AccumulateFilter,
    FinancialFilter,
)



class FutuAPI:

    # DATA_PATH = "/Users/joseph/Dropbox/code/stat-arb/data"
    DATA_PATH = "/home/atabet/projects/data"

    HK_EQUITY_AM_START = timer(9, 30, 0)
    HK_EQUITY_AM_END = timer(12, 0, 0)
    HK_EQUITY_PM_START = timer(13, 0, 0)
    HK_EQUITY_PM_END = timer(16, 0, 0)

    def __init__(self):
        self.subscribe_data = dict()
        self.broker_queue = dict()

    def __enter__(self):
        self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        self.connect_quote()
        return self

    def __exit__(self, type, value, trace):
        self.quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
        print("Close quote context!")

    def subscribe(self, codes:List[str], sub_types:List[SubType], sub_push:bool):
        ret_sub, err_message = self.quote_ctx.subscribe(codes, sub_types, subscribe_push=sub_push)
        if ret_sub==RET_ERROR:
            raise ValueError(f"subscribe error: {err_message}")

    def get_global_state(self)->dict:
        """
        获取全局市场状态

        https://openapi.futunn.com/futu-api-doc/quote/get-global-state.html
        :return: (0, {'market_sz': 'CLOSED', 'market_us': 'PRE_MARKET_BEGIN', 'market_sh': 'CLOSED',
        'market_hk': 'CLOSED', 'market_hkfuture': 'FUTURE_DAY_OPEN', 'market_usfuture': 'FUTURE_OPEN',
        'server_ver': '217', 'trd_logined': True, 'timestamp': '1602491044', 'qot_logined': True,
        'local_timestamp': 1602491044.555623, 'program_status_type': 'READY', 'program_status_desc': ''})
        """
        ret, data = self.quote_ctx.get_global_state()
        if ret == RET_OK:
            return data
        raise ValueError(f"get_global_state error: {data}")

    def get_capital_distribution(self, code:str="HK.00700"):
        """
        获取资金分布

        :param code: 股票代号
        :return:
        """
        ret, data = self.quote_ctx.get_capital_distribution(code)
        if ret == RET_OK:
            return data
        else:
            print('error:', data)

    def get_capital_flow(self, code:str="HK.00700"):
        """
        获取资金流向

        :param code: 股票代号
        :return:
        """
        ret, data = self.quote_ctx.get_capital_flow(code)
        if ret == RET_OK:
            return data
        else:
            print('error:', data)

    def get_broker_queue(self, code:str="HK.00700"):
        """
        获取实时经纪队列

        :param code:
        :return:
        """
        # 如果通过推送获取数据，直接在缓存里提取最新的copy
        if code in self.broker_queue:
            return self.broker_queue[code]

        # 否则通过富途服务器获取。先订阅经纪队列类型。订阅成功后FutuOpenD将持续收到服务器的推送，False代表暂时不需要推送给脚本
        if (code not in self.subscribe_data) :
            ret_sub, err_message = self.quote_ctx.subscribe([code], [SubType.BROKER], subscribe_push=False)
            if ret_sub!=RET_OK:
                print(f"获取实时经纪队列(get_broker_queue)失败, {err_message}")
            self.subscribe_data[code] = dict()
            self.subscribe_data[code][SubType.BROKER] = True
        elif (SubType.BROKER not in self.subscribe_data[code]):
            ret_sub, err_message = self.quote_ctx.subscribe([code], [SubType.BROKER], subscribe_push=False)
            if ret_sub!=RET_OK:
                print(f"获取实时经纪队列(get_broker_queue)失败, {err_message}")
            self.subscribe_data[code][SubType.BROKER] = True

        ret, bid_frame_table, ask_frame_table = self.quote_ctx.get_broker_queue(code)  # 获取一次经纪队列数据
        if ret == RET_OK:
            return bid_frame_table, ask_frame_table
        else:
            print('error:', bid_frame_table)

    def process_broker_queue(self, data:pd.DataFrame):
        bid_broker, ask_broker = data
        codes = list(bid_broker["code"].unique())
        assert len(codes)==1, f"broker_queue pushback 不是合法的数据：{codes}"
        code = codes[0]
        self.broker_queue[code] = (bid_broker, ask_broker)

    def connect_quote(self):
        class BrokerQueueHandler(BrokerHandlerBase):
            api = self
            def on_recv_rsp(self, rsp_pb):
                ret_code, err_or_stock_code, data = super(BrokerQueueHandler, self).on_recv_rsp(rsp_pb)
                if ret_code != RET_OK:
                    print("BrokerTest: error, msg: {}".format(err_or_stock_code))
                    return RET_ERROR, data
                api.process_broker_queue(data) # BrokerQueueHandler自己的处理逻辑
                return RET_OK, data
        self.quote_ctx.set_handler(BrokerQueueHandler())
        self.quote_ctx.start()


    def get_history_kl_quota(self, get_detail:bool=False):
        """
        获取历史 K 线额度使用明细

        接口限制
        ------
        我们会根据您账户的资产和交易的情况，下发历史 K 线额度。因此，30 天内您只能获取有限只股票的历史 K 线数据。具体规则参见 API 用户额度 。
        您当日消耗的历史 K 线额度，会在 30 天后自动释放。
        https://openapi.futunn.com/futu-api-doc/quote/get-history-kl-quota.html
        :param get_detail: 设置True代表需要返回详细的拉取历史K 线的记录
        :return: 例子 (1, 99, [{'code': 'HK.00700', 'request_time': '2020-03-27 19:15:57'}])
        """
        ret, data = self.quote_ctx.get_history_kl_quota(get_detail=get_detail)
        if ret == RET_OK:
            return data
        else:
            print('error:', data)


    def request_history_kline(self,
                              code:str,
                              start:str,
                              end:str,
                              ktype:KLType=KLType.K_DAY,
                              autype:AuType=AuType.QFQ,
                              fields:List[KL_FIELD]=[KL_FIELD.ALL],
                              max_count:int=500,
                              extended_time:bool=False):
        """
        获取历史 K 线

        接口限制
        -------
        我们会根据您账户的资产和交易的情况，下发历史 K 线额度。因此，30 天内您只能获取有限只股票的历史 K 线数据。具体规则参见 API 用户额度 。您当日消耗的
        历史 K 线额度，会在 30 天后自动释放。
        每 30 秒内最多请求 60 次历史 K 线接口。注意：如果您是分页获取数据，此限频规则仅适用于每只股票的首页，后续页请求不受限频规则的限制。
        分 K 提供最近 2 年数据，日 K 及以上提供最近 10 年的数据。
        美股盘前和盘后 K 线仅支持 60 分钟及以下级别。由于美股盘前和盘后时段为非常规交易时段，此时段的 K 线数据可能不足 2 年。
        https://openapi.futunn.com/futu-api-doc/quote/request-history-kline.html
        :param code: 'HK.00700'
        :param start: '2019-09-11'
        :param end: '2019-09-18'
        :param ktype: KLType.K_DAY,
        :param autype: AuType.QFQ,
        :param fields: [KL_FIELD.ALL],
        :param max_count: 500,
        :param extended_time: False
        :return:
        """
        ret, data, page_req_key = self.quote_ctx.request_history_kline(
            code=code,
            start=start,
            end=end,
            ktype=ktype,
            autype=autype,
            fields=fields,
            max_count=max_count,
            extended_time=extended_time,
        )  # 每页max_count个，请求第一页
        if ret == RET_OK:
            yield data
        else:
            print('error:', data)
            return
        while page_req_key != None:  # 请求后面的所有结果
            print('*************************************')
            ret, data, page_req_key = self.quote_ctx.request_history_kline(
                code=code,
                start=start,
                end=end,
                ktype=ktype,
                autype=autype,
                fields=fields,
                max_count=max_count,
                extended_time=extended_time,
                page_req_key=page_req_key
            )  # 请求翻页后的数据
            if ret == RET_OK:
                yield data
            else:
                print('error:', data)
                return

    def get_rehab(self, code:str="HK.00700"):
        """
        获取复权因子

        接口限制
        ------
        每 30 秒内最多请求 60 次获取复权因子接口。
        https://openapi.futunn.com/futu-api-doc/quote/get-rehab.html
        :param market:
        :param security:
        :return:
        """
        ret, data = self.quote_ctx.get_rehab(code)
        if ret == RET_OK:
            return data
        else:
            print('error:', data)

    def get_cur_kline(self,
                      code_list:List[str]=["00700.HK"],
                      ktype_list:List[SubType]=[SubType.K_1M],
                      num:int=1000,
                      autype=AuType.QFQ):
        """
        获取实时 K 线

        :param code_list: 股票代码列表
        :param ktype_list: K 线类型列表
        :param num: K 线数据个数，最多 1000 根
        :param autype: 复权类型
        :return:
        """
        ret_sub, err_message = self.quote_ctx.subscribe(code_list, ktype_list, subscribe_push=False)
        # 先订阅K 线类型。订阅成功后FutuOpenD将持续收到服务器的推送，False代表暂时不需要推送给脚本
        if ret_sub == RET_OK:  # 订阅成功
            ret_data = []
            for code, ktype in zip(code_list, ktype_list):
                ret, data = self.quote_ctx.get_cur_kline(code, num, ktype, autype)  # 获取港股00700最近2个K线数据
                if ret == RET_OK:
                    ret_data.append(data)
                else:
                    print('error:', data)
                    ret_data.append(None)
            return ret_data
        else:
            print('subscription failed', err_message)

    def record_cur_kline(self,
                         code_list:List[str]=["00700.HK"],
                         ktype_list:List[SubType]=[SubType.K_1M],
                         record_time:int=28800): # 3600*8
        """
        记录实时 K 线 (非futu原有api)

        :param market: 市场
        :param security: 股票代码
        :param ktype: K 线类型
        :return:
        """

        handler = CurKlineHandler()
        self.quote_ctx.set_handler(handler)  # 设置实时摆盘回调
        self.quote_ctx.subscribe(code_list, ktype_list)  # 订阅K线数据类型，FutuOpenD开始持续收到服务器的推送
        time.sleep(record_time)  # 设置脚本接收FutuOpenD的推送持续时间
        self.quote_ctx.unsubscribe(code_list, ktype_list) # 反订阅K线数据类型（1分钟后生效）

    def query_subscription(self, is_all_conn:bool=True):
        """

        :param is_all_conn: 是否返回所有连接的订阅状态。True：返回所有连接的订阅状态；False：只返回当前连接的订阅状态
        :return:
        """
        ret, data = self.quote_ctx.query_subscription(is_all_conn=is_all_conn)
        if ret == RET_OK:
            return data
        else:
            print('error:', data)

    def get_owner_plate(self, code_list:List):
        """
        获取股票所属板块

        :param code_list:
        :return:
        """
        ret, data = self.quote_ctx.get_owner_plate(code_list)
        if ret == RET_OK:
            return data
        else:
            print('error:', data)

    def get_plate_list(self, market:Market, plate_class:Plate):
        """
        获取板块列表

        :param market:
        :param plate_class:
        :return:
        """
        ret, data = self.quote_ctx.get_plate_list(market, plate_class)
        if ret == RET_OK:
            return data
        else:
            print('error:', data)

    def get_plate_stock(self, plate_code:str, sort_field:SortField=SortField.CODE, ascend:bool=True):
        """
        获取板块内股票列表

        :param plate_code:
        :param sort_field:
        :param ascend:
        :return:
        """
        ret, data = self.quote_ctx.get_plate_stock(plate_code)
        if ret == RET_OK:
            return data
        else:
            raise ValueError(f'error: {data}')

    def get_stock_filter(self,
                         market:Market,
                         filter_list:List[Union[SimpleFilter,AccumulateFilter,FinancialFilter]],
                         plate_code:str=None,
                         begin:int=0,
                         num:int=200):
        """
        条件选股

        :param market:
        :param filter_list:
        :param plate_code:
        :param begin:
        :param num:
        :return:
        """

        ret, ls = self.quote_ctx.get_stock_filter(market, filter_list, plate_code=plate_code, begin=begin, num=num)  # 对香港市场的股票做简单筛选
        if ret == RET_OK:
            # last_page, all_count, ret_list = ls
            # print(len(ret_list), all_count, ret_list)
            # for item in ret_list:
            #     print(item.stock_code)  # 取其中的股票代码
            return ls
        else:
            raise ValueError(f'error: {ls}')

    def save_history_kline(self,
                           code: str,
                           start: str = None,
                           end: str = None,
                           ktype: KLType = KLType.K_DAY,
                           autype: AuType = AuType.QFQ,
                           fields: List[KL_FIELD] = [KL_FIELD.ALL],
                           max_count: int = 5000,
                           extended_time: bool = False):


        # 检查开始和结束时间
        now = datetime.now()
        if end is None:
            end_dt = now
            end = datetime.strftime(end_dt, "%Y-%m-%d")
        else:
            end_dt = datetime.strptime(end, "%Y-%m-%d")

        if start is None:
            start_dt = now - relativedelta(months=25)
            start = datetime.strftime(start_dt, "%Y-%m-%d")
        else:
            start_dt = datetime.strptime(start, "%Y-%m-%d")

        assert start_dt<end_dt, "start>=end, invalid time input!"


        history_kline = self.request_history_kline(code=code,
                                                  start=start,
                                                  end=end,
                                                  ktype=ktype,
                                                  max_count=max_count,
                                                  fields=fields, # [KL_FIELD.DATE_TIME, KL_FIELD.CLOSE]
        )

        for n, kl in enumerate(history_kline):
            if "klines" not in locals():
                klines = kl
            else:
                klines = klines.append(kl, ignore_index=True)

            dts = list(set([t.split(" ")[0] for t in klines["time_key"]]))
            dts.sort()
            if len(dts) == 0:
                print(f"No data available for {code}")
                break
            if len(dts) > 1:
                for dt in dts[:-1]:
                    df = klines[
                        (klines["time_key"] >= f"{dt} 00:00:00") &
                        (klines["time_key"] <= f"{dt} 23:59:59")
                        ]
                    if not os.path.exists(f"{self.DATA_PATH}/k_line/{str(ktype)}/{code}"):
                        os.mkdir(f"{self.DATA_PATH}/k_line/{str(ktype)}/{code}")
                    df.to_csv(f"{self.DATA_PATH}/k_line/{str(ktype)}/{code}/{dt}.csv", index=False)
                    print(f"{code}/{dt}.csv saved.")

            klines = klines[klines["time_key"] >= f"{dts[-1]} 00:00:00"]

        if not klines.empty:
            klines.to_csv(f"{self.DATA_PATH}/k_line/{str(ktype)}/{code}/{dts[-1]}.csv", index=False)
            print(f"{code}/{dts[-1]}.csv saved.")

    def is_hk_equity_market_time(self, cur_datetime: datetime) -> bool:
        """If current datetime is within market open time"""
        return (
                self.HK_EQUITY_AM_START <= cur_datetime.time() <= self.HK_EQUITY_AM_END or
                self.HK_EQUITY_PM_START <= cur_datetime.time() <= self.HK_EQUITY_PM_END
        )

    def next_hk_equity_market_time(self, cur_datetime: datetime) -> datetime:
        """Return next market open time"""
        if cur_datetime.time() < self.HK_EQUITY_AM_START:
            return datetime(
                cur_datetime.year,
                cur_datetime.month,
                cur_datetime.day,
                self.HK_EQUITY_AM_START.hour,
                self.HK_EQUITY_AM_START.minute,
                self.HK_EQUITY_AM_START.second,
            )
        elif cur_datetime.time() < self.HK_EQUITY_PM_START:
            return datetime(
                cur_datetime.year,
                cur_datetime.month,
                cur_datetime.day,
                self.HK_EQUITY_PM_START.hour,
                self.HK_EQUITY_PM_START.minute,
                self.HK_EQUITY_PM_START.second,
            )
        else:
            return None

    def get_stock_basicinfo(self)->pd.DataFrame:
        """stock info"""
        ret_code, data = self.quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK)
        if ret_code:
            print(f"Fail to get stock basicinfo: {data}")
            return
        return data

class CurKlineHandler(CurKlineHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(CurKlineHandler,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            # TODO: 存入数据库
            print("CurKlineTest: error, msg: %s" % data)
            return RET_ERROR, data
        print(f"{datetime.now()} ", data) # CurKlineTest自己的处理逻辑
        return RET_OK, data




if __name__=="__main__":

    with FutuAPI() as api:
        DATA_PATH = api.DATA_PATH
        # 确认csv文件已经存在
        # plate_stock = pd.read_csv(f"{DATA_PATH}/stock_list/HK.BK1050-2021-02-25.csv")
        codes = ["HK.01157", "HK.01117", "HK.00981",
                 "HK.01024", "HK.09633", "HK.02359",
                 "HK.09922", "HK.01810", "HK.03968",
                 "HK.02319", "HK.00285", "HK.06618",
                 "HK.00763", "HK.02269", "HK.09988",
                 "HK.09926", "HK.01347", "HK.03690",
                 "HK.09626", "HK.09888",
                 "HK.800000"]
        # codes = ["SH.000300"]
        for code in codes: # ["HK.01157", "HK.01117", "HK.00981"]: # plate_stock["code"].values[:]:
            # history_kline = api.request_history_kline(code=code,
            #                                           start="2019-01-01",
            #                                           end="2021-03-17",
            #                                           ktype=KLType.K_1M,
            #                                           max_count=5000,
            #                                           fields=[KL_FIELD.DATE_TIME, KL_FIELD.CLOSE])

            # 保存历史k线
            api.save_history_kline(code=code,
                                   start="2021-08-13",
                                   # end="2021-03-15",
                                   ktype=KLType.K_1M,
                                   fields=[KL_FIELD.ALL]
            )


        # 查询公司复权历史
        # rehab = api.get_rehab("HK.00700")

        # 一次性获取实时k线
        # rt_kline_data = api.get_cur_kline(
        #     code_list=["HK.02359", "HK.02269"],
        #     ktype_list=[SubType.K_1M, SubType.K_1M],
        #     num = 3
        # )

        # 记录实时k线
        # api.record_cur_kline(
        #     code_list = ["HK.02359", "HK.02269"],
        #     ktype_list = [SubType.K_1M, SubType.K_1M],
        #     record_time = 300
        # )

        # 获取板块列表
        # owner_plate = api.get_owner_plate(["HK.02359"])
        # plate_list = api.get_plate_list(Market.HK, Plate.INDUSTRY)
        # plate_stock = api.get_plate_stock("HK.BK1050")
        # plate_stock.to_csv(f"{DATA_PATH}/stock_list/HK.BK1050-{datetime.strftime(datetime.today(), '%Y-%m-%d')}.csv", index=False)
        # print()

        # 筛选股票
        # simple_filter1 = SimpleFilter()
        # simple_filter1.filter_min = 0
        # simple_filter1.filter_max = 20000
        # simple_filter1.stock_field = StockField.LOT_PRICE
        # simple_filter1.is_no_filter = False
        #
        #
        # accumulate_filter2 = AccumulateFilter()
        # accumulate_filter2.filter_min = 0.3
        # accumulate_filter2.filter_max = 10
        # accumulate_filter2.stock_field = StockField.TURNOVER_RATE
        # accumulate_filter2.is_no_filter = False
        # accumulate_filter2.days = 30
        # accumulate_filter2.sort = SortDir.ASCEND
        #
        # last_page, all_count, stocks = api.get_stock_filter(
        #     Market.HK,
        #     [simple_filter1, accumulate_filter2],
        #     plate_code="HK.BK1050"
        # )
        # stock_list = []
        # for stock in stocks:
        #     stock_list.append(stock.stock_code)
        # print(stock_list)

    print()