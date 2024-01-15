from typing import Any, Dict, List, Literal, NamedTuple, Optional
from urllib.request import urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from argparse import ArgumentParser


class Namespace(NamedTuple):
    savepath: str
    limit: int
    format: Literal['json', 'txt']
    type: Optional[Literal['http', 'socks4', 'socks5']]
    level: Optional[Literal['anonymous', 'elite']]
    api: Optional[str]
    https: Optional[bool]
    post: Optional[bool]
    user_agent: Optional[bool]

    def to_dict(self) -> Dict[str, Any]:
        return self._asdict()


def parse_args(args: Optional[List[str]] = None) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--savepath', type=str, dest='savepath', help='file to write the result', required=True)
    parser.add_argument('--amount', type=int, dest='limit', help='the number of proxies to save (max-free:2, max-premium: 30)', default=1)
    parser.add_argument('--format', type=str, dest='format', help='how to format the proxy output (json, txt)', default='txt')
    parser.add_argument('--type', type=str, nargs='?', dest='type', help='proxy protocol (http, socks4, socks5)')
    parser.add_argument('--level', type=str, nargs='?', dest='level', help='the proxy level (anonymous, elite)')
    parser.add_argument('--apikey', type=str, dest='api', help='the apikey of pubproxy.com')
    parser.add_argument('--https', dest='https', action='store_true', help='supports HTTPS request')
    parser.add_argument('--no-https', dest='https', action='store_false', help='does not support HTTPS request')
    parser.add_argument('--post', dest='post', action='store_true', help='supports POST request')
    parser.add_argument('--no-post', dest='post', action='store_false', help='supports POST request')
    parser.add_argument('--user-agent', dest='user_agent', action='store_true', help='supports User-Agent request')
    parser.add_argument('--no-user-agent', dest='user_agent', action='store_false', help='supports User-Agent request')
    parser.set_defaults(https=None, post=None, user_agent=None)
    arguments = parser.parse_args(args)
    return Namespace(**vars(arguments))


def main(namespace: Namespace) -> None:
    api = "http://pubproxy.com/api/proxy"
    params: Dict[str, Any] = {}
    for key, value in namespace.to_dict().items():
        if value is None or key in ['savepath']:
            continue
        if isinstance(value, (int, bool)):
            value = str(value).lower()
        params[key] = value
    api += '?' + '&'.join([k+'='+quote(v) for k, v in params.items()])
    try:
        response = urlopen(api)
        if response.status != 200:
            raise HTTPError(response.url, response.code, response.msg, response.headers, response.fp)
    except HTTPError as e:
        if e.code == 503:
            raise RuntimeError(f'{e.code} - Daily limit reached') from None
        raise RuntimeError(f'{e.code} - {e.reason}') from None
    with open(namespace.savepath, 'wb') as f:
        f.write(response.read())


if __name__ == '__main__':
    args = parse_args()
    main(args)
