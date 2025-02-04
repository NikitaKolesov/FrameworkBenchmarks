from toolset.benchmark.test_types.framework_test_type import FrameworkTestType
from toolset.benchmark.fortune_html_parser import FortuneHTMLParser
from toolset.benchmark.test_types.verifications import (
    basic_body_verification,
    verify_headers,
)


class FortuneTestType(FrameworkTestType):
    def __init__(self, config):
        self.fortune_url = ""
        kwargs = {
            "name": "fortune",
            "accept_header": self.accept("html"),
            "requires_db": True,
            "args": ["fortune_url"],
        }
        FrameworkTestType.__init__(self, config, **kwargs)

    def get_url(self):
        return self.fortune_url

    def verify(self, base_url):
        """
        Parses the given HTML string and asks the
        FortuneHTMLParser whether the parsed string is a
        valid fortune response
        """

        url = base_url + self.fortune_url
        headers, body = self.request_headers_and_body(url)

        _, problems = basic_body_verification(body, url, is_json_check=False)

        if len(problems) > 0:
            return problems

        parser = FortuneHTMLParser()
        parser.feed(body)
        (valid, diff) = parser.isValidFortune(self.name, body)

        if valid:
            problems += verify_headers(
                self.request_headers_and_body, headers, url, should_be="html"
            )

            if len(problems) == 0:
                return [("pass", "", url)]
            else:
                return problems
        else:
            failures = []
            failures.append(("fail", "Invalid according to FortuneHTMLParser", url))
            failures += self._parseDiffForFailure(diff, failures, url)
            return failures

    def _parseDiffForFailure(self, diff, failures, url):
        """
        Example diff:

        --- Valid
        +++ Response
        @@ -1 +1 @@

        -<!doctype html><html><head><title>Fortunes</title></head><body><table>
        +<!doctype html><html><head><meta></meta><title>Fortunes</title></head><body><div><table>
        @@ -16 +16 @@
        """

        problems = []

        # Catch exceptions because we are relying on internal code
        try:
            current_neg = []
            current_pos = []
            for line in diff[3:]:
                if line[0] == "+":
                    current_neg.append(line[1:])
                elif line[0] == "-":
                    current_pos.append(line[1:])
                elif line[0] == "@":
                    problems.append(
                        (
                            "fail",
                            "`%s` should be `%s`"
                            % ("".join(current_neg), "".join(current_pos)),
                            url,
                        )
                    )
            if len(current_pos) != 0:
                problems.append(
                    (
                        "fail",
                        "`%s` should be `%s`"
                        % ("".join(current_neg), "".join(current_pos)),
                        url,
                    )
                )
        except:
            # If there were errors reading the diff, then no diff information
            pass
        return problems

    def get_script_name(self):
        return "concurrency.sh"

    def get_script_variables(self, name, url):
        return {
            "max_concurrency": max(self.config.concurrency_levels),
            "name": name,
            "duration": self.config.duration,
            "levels": " ".join(
                "{}".format(item) for item in self.config.concurrency_levels
            ),
            "server_host": self.config.server_host,
            "url": url,
            "accept": "application/json,text/html;q=0.9,application/xhtml+xml;q=0.9,application/xml;q=0.8,*/*;q=0.7",
        }
