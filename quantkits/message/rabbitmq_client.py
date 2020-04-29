# -*- coding: utf-8 -*-
# @Time    : 11/14/2019 2:42 PM
# @Author  : Joseph Chen
# @Email   : joseph.chen@magnumwm.com
# @FileName: rabbitmq_client.py
# @Software: PyCharm

import json
import re
import threading
from decimal import Decimal
from functools import partial

import pika


market_client = None


class MarketClient(object):
    _instance_lock = threading.Lock()
    _instrument_lock = threading.Lock()

    tick_cb = NotImplemented
    orderbook_cb = NotImplemented
    order_cb = NotImplemented
    execution_cb = NotImplemented

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, end_point='localhost'):
        """
        :param regions: Example  'HK,CN' or 'CN' or ...
        :param categories: Example      '10,20' or '10' or...
        """
        self._init_rq_channel()

        self.orderbook_data = {}
        self.tick_data = {}
        self.trading_order_data = {}
        self.trading_execution_data = {}

    def _init_rq_channel(self):
        credentials = pika.PlainCredentials('atabet', 'atabetRabbit')
        connection_param = pika.ConnectionParameters(
            host='localhost',
            port=5673,
            credentials=credentials,
            virtual_host='vhost'
        )
        self.connection = pika.BlockingConnection(connection_param)
        self.channel = self.connection.channel()

    def callback(self, ch, method, properties, body, message_type=None):
        """Algorithm team has to define and implement their own requirement

        Explanation:
        - "ch" is the "channel" over which the communication is happening.
        - "method" is meta information regarding the message delivery
        - "properties" of the message are user-defined properties on the message.
        - "body" == "message"
        """
        # print("%r:%r" % (method.routing_key, json.loads(body)))
        data = json.loads(body)
        iuid = method.routing_key.replace('.', '_')
        callback = NotImplemented
        if message_type == 'orderbook':
            self.orderbook_data[method.routing_key] = data
            callback = self.orderbook_cb
            # print("orderbook_data: ", data)
        elif message_type == 'tick':
            self.tick_data[method.routing_key] = data
            callback = self.tick_cb
            # print("tick_data: ", data)
        elif message_type == 'trading.order':
            self.trading_order_data[method.routing_key] = data
            callback = self.order_cb
            # print(self.trading_order_data)
        elif message_type == 'trading.execution':
            self.trading_execution_data[method.routing_key] = data
            callback = self.execution_cb
            # print(self.trading_execution_data)

        if callback:
            try:
                callback(iuid, data)
            except:
                pass

    def real_time_data(self, iuid_list, orderbook=False, broker_id=None, account_id=None):
        """
        subscribe the info (i.e.., orderbook, tick, trading.order, trading.execution) of each iuid automatically
        """
        # stop the channel consuming thread
        self.channel.stop_consuming()
        iuids = [id.replace("_", ".") for id in iuid_list]

        # tick queue
        result = self.channel.queue_declare(exclusive=True, auto_delete=True)
        queue_name_tick = result.method.queue
        for binding_key in iuids:
            self.channel.queue_bind(
                exchange='market.tick',
                queue=queue_name_tick,
                routing_key=binding_key
            )
        tick_consume = partial(self.callback, message_type='tick')
        self.channel.basic_consume(
            tick_consume,
            queue=queue_name_tick,
            no_ack=True
        )

        # orderbook queue
        if orderbook:
            result = self.channel.queue_declare(exclusive=True, auto_delete=True)
            queue_name_orderbook = result.method.queue
            for binding_key in iuids:
                self.channel.queue_bind(
                    exchange='market.orderbook',
                    queue=queue_name_orderbook,
                    routing_key=binding_key
                )
            orderbook_consume = partial(self.callback, message_type='orderbook')
            self.channel.basic_consume(
                orderbook_consume,
                queue=queue_name_orderbook,
                no_ack=True
            )

        # trading_order and trading_execution
        if broker_id is not None and account_id is not None:
            result = self.channel.queue_declare(exclusive=True, auto_delete=True)
            queue_name_trading_order = result.method.queue
            result = self.channel.queue_declare(exclusive=True, auto_delete=True)
            queue_name_trading_execution = result.method.queue
            self.channel.queue_bind(
                exchange='trading',
                queue=queue_name_trading_order,
                routing_key="order.{}.{}".format(broker_id, account_id)
            )
            self.channel.queue_bind(
                exchange='trading',
                queue=queue_name_trading_execution,
                routing_key="execution.{}.{}".format(broker_id, account_id)
            )
            trading_consume = partial(self.callback, message_type='trading.order')
            self.channel.basic_consume(
                trading_consume,
                queue=queue_name_trading_order,
                no_ack=True
            )

            trading_consume = partial(self.callback, message_type='trading.execution')
            self.channel.basic_consume(
                trading_consume,
                queue=queue_name_trading_execution,
                no_ack=True
            )

        t = threading.Thread(target=self.channel.start_consuming)
        t.setDaemon(True)
        t.start()


def init_client(end_point='https://market.aqumon.com'):
    global market_client
    if market_client is None:
        market_client = MarketClient(end_point=end_point)
    return market_client


if __name__ == '__main__':
    # demo
    # market_client = init_client(end_point='https://market.aqumon.com', regions='WW', categories='10')
    market_client = init_client(end_point='localhost')
    from quantkits import time

    # date = '2018-12-17'
    region = 'HK'
    # print('is biz day:')
    # print(market_client.is_biz_day(date=date, region=region))
    #
    # print('next or pre T+x biz day(T={0}):'.format(date))
    # print(market_client.get_biz_day(date=date, region=region, days_offset=1))
    # print(market_client.get_biz_day(date=date, region=region, days_offset=2))
    # print(market_client.get_biz_day(date=date, region=region, days_offset=-2))
    #
    # print('validate iuids:')
    # print(market_client.validate_iuids(iuids=['AE_10_ADCB', 'US_10_IEFA', 'FALSE_IUID']))
    #
    # print('query iuid:')
    # print(market_client.query_iuid(region='US', category='10', ticker='IEFA'))
    # print(market_client.query_iuid(region='US', category='30').keys())
    # # false
    # print(market_client.query_iuid(region='1', category='10', ticker='IEFA'))
    # # false
    # print(market_client.query_iuid(region='1'))
    #
    # print('access single iuid')
    # # print(market_client.instruments['US_10_VTI'])
    #
    # print('transfer broker local symbol')
    # print(market_client.transfer_broker_local_symbol(['US_10_IEFA'], broker_id=1))
    #
    # print('historical quotes')
    # print(market_client.historical_quotes(iuids=['US_10_IEFA', 'CN_10_000001'], start_date_ts=1543203902953, end_date_ts=1545028974000,
    #                                       tags=[4], period='D'))
    #
    # print('historical events')
    # print(market_client.historical_events(iuids=['US_10_IEFA'], start_time=1543203902953, end_time=1545028974000))
    #
    # print('snapshot data')
    # print(market_client.snapshot_data(['HK_10_3115']))
    #
    # print('fx')
    # print(market_client.fx('USD', 'HKD'))
    # print(market_client.fx('HKD', 'USD'))

    # market_client.real_time_data(['HK_10_700'], orderbook=True)
    # time.sleep(1)
    #
    # print(marketlib.get_current_subscribed_list(region, category='10'))
    #
    # for i in range(3600):
    #     print('tick_data: {0}'.format(market_client.tick_data))
    #     print('orderbook_data: {0}'.format(market_client.orderbook_data))
    #     time.sleep(1)