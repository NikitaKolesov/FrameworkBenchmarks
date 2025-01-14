from toolset.benchmark.test_types.framework_test_type import FrameworkTestType
from toolset.benchmark.test_types.verifications import verify_query_cases


class CachedQueryTestType(FrameworkTestType):
    def __init__(self, config):
        self.cached_query_url = ""
        kwargs = {
            "name": "cached_query",
            "accept_header": self.accept("json"),
            "requires_db": True,
            "args": ["cached_query_url"],
        }
        FrameworkTestType.__init__(self, config, **kwargs)

    def get_url(self):
        return self.cached_query_url

    def verify(self, base_url):
        """
        Validates the response is a JSON array of
        the proper length, each JSON Object in the array
        has keys 'id' and 'randomNumber', and these keys
        map to integers. Case insensitive and
        quoting style is ignored
        """

        url = base_url + self.cached_query_url
        cases = [
            ("2", "fail"),
            ("0", "fail"),
            ("foo", "fail"),
            ("501", "warn"),
            ("", "fail"),
        ]

        problems = verify_query_cases(self, cases, url)

        if len(problems) == 0:
            return [("pass", "", url + case) for case, _ in cases]
        else:
            return problems

    def get_script_name(self):
        return "query.sh"

    def get_script_variables(self, name, url):
        return {
            "max_concurrency": max(self.config.concurrency_levels),
            "name": name,
            "duration": self.config.duration,
            "levels": " ".join(
                "{}".format(item) for item in self.config.cached_query_levels
            ),
            "server_host": self.config.server_host,
            "url": url,
            "accept": "application/json,text/html;q=0.9,application/xhtml+xml;q=0.9,application/xml;q=0.8,*/*;q=0.7",
        }
