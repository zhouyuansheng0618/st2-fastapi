# -*- coding: utf-8 -*- 
# @Time : 2022/6/1 17:51 
# @Author : zhouys618@163.com 
# @File : config.py 
# @desc:

from oslo_config import cfg
import os

DEFAULT_CONFIG_FILE_PATH = os.environ.get("ST2_CONFIG_PATH", "./config.conf")
VERSION_STRING = "StackStorm v%s" % (3.6)
# 注册命令行参数选项
def do_register_opts(opts, group=None, ignore_errors=False):
    try:
        cfg.CONF.register_opts(opts, group=group)
    except:
        if not ignore_errors:
            raise


def register_opts(ignore_errors=False):

    mongodb_opts = [
        cfg.StrOpt("host", default="127.0.0.1", help="host of db server"),
        cfg.IntOpt("port", default=27017, help="port of db server"),
        cfg.StrOpt("db_name", default="test", help="name of database"),
        cfg.StrOpt("username", help="username for db login"),
        cfg.StrOpt("password", help="password for db login"),
        cfg.IntOpt(
            "connection_timeout",
            default=3 * 1000,
            help="Connection and server selection timeout (in ms).",
        ),
        cfg.IntOpt(
            "connection_retry_max_delay_m",
            default=3,
            help="Connection retry total time (minutes).",
        ),
        cfg.IntOpt(
            "connection_retry_backoff_max_s",
            default=10,
            help="Connection retry backoff max (seconds).",
        ),
        cfg.IntOpt(
            "connection_retry_backoff_mul",
            default=1,
            help="Backoff multiplier (seconds).",
        ),
        cfg.BoolOpt(
            "ssl", default=False, help="Create the connection to mongodb using SSL"
        ),
        cfg.StrOpt(
            "ssl_keyfile",
            default=None,
            help="Private keyfile used to identify the local connection against MongoDB.",
        ),
        cfg.StrOpt(
            "ssl_certfile",
            default=None,
            help="Certificate file used to identify the localconnection",
        ),
        cfg.StrOpt(
            "ssl_cert_reqs",
            default=None,
            choices="none, optional, required",
            help="Specifies whether a certificate is required from the other side of the "
            "connection, and whether it will be validated if provided",
        ),
        cfg.StrOpt(
            "ssl_ca_certs",
            default=None,
            help="ca_certs file contains a set of concatenated CA certificates, which are "
            "used to validate certificates passed from MongoDB.",
        ),
        cfg.BoolOpt(
            "ssl_match_hostname",
            default=True,
            help="If True and `ssl_cert_reqs` is not None, enables hostname verification",
        ),
        cfg.StrOpt(
            "authentication_mechanism",
            default=None,
            help="Specifies database authentication mechanisms. "
            "By default, it use SCRAM-SHA-1 with MongoDB 3.0 and later, "
            "MONGODB-CR (MongoDB Challenge Response protocol) for older servers.",
        ),
        cfg.StrOpt(
            "compressors",
            default="",
            help="Comma delimited string of compression algorithms to use for transport level "
            "compression. Actual algorithm will then be decided based on the algorithms "
            "supported by the client and the server. For example: zstd. Defaults to no "
            "compression. Keep in mind that zstd is only supported with MongoDB 4.2 and later.",
        ),
        cfg.IntOpt(
            "zlib_compression_level",
            default="",
            help="Compression level when compressors is set to zlib. Valid calues are -1 to 9. "
            "Defaults to 6.",
        ),
    ]

    do_register_opts(mongodb_opts, 'mongo', ignore_errors)


def parse_args(args=None, ignore_errors=False):
    register_opts(ignore_errors=ignore_errors)
    cfg.CONF(
        args=args,
        version=VERSION_STRING,
        default_config_files=[DEFAULT_CONFIG_FILE_PATH],
    )
