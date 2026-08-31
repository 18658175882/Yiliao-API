from http.server import BaseHTTPRequestHandler
import json

RECORDS = [
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"协和","医生":"王**","拜访类型":"正式拜访","时长分钟":45},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"协和","医生":"李**","拜访类型":"正式拜访","时长分钟":40},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"北大人民","医生":"赵**","拜访类型":"正式拜访","时长分钟":50},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"北大人民","医生":"钱**","拜访类型":"学术拜访","时长分钟":35},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"阜外","医生":"孙**","拜访类型":"正式拜访","时长分钟":30},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"阜外","医生":"周**","拜访类型":"正式拜访","时长分钟":40},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"朝阳","医生":"吴**","拜访类型":"正式拜访","时长分钟":45},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"朝阳","医生":"郑**","拜访类型":"学术拜访","时长分钟":25},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"天坛","医生":"冯**","拜访类型":"正式拜访","时长分钟":50},
    {"代表":"张三","月份":"2026-06","药名":"克罗凯","医院":"天坛","医生":"陈**","拜访类型":"正式拜访","时长分钟":40},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"协和","医生":"王**","拜访类型":"正式拜访","时长分钟":50},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"协和","医生":"李**","拜访类型":"正式拜访","时长分钟":45},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"北大人民","医生":"赵**","拜访类型":"正式拜访","时长分钟":55},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"北大人民","医生":"黄**","拜访类型":"正式拜访","时长分钟":40},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"阜外","医生":"孙**","拜访类型":"正式拜访","时长分钟":35},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"阜外","医生":"周**","拜访类型":"正式拜访","时长分钟":45},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"朝阳","医生":"吴**","拜访类型":"正式拜访","时长分钟":50},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"朝阳","医生":"郑**","拜访类型":"学术拜访","时长分钟":30},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"天坛","医生":"冯**","拜访类型":"正式拜访","时长分钟":55},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"天坛","医生":"陈**","拜访类型":"正式拜访","时长分钟":45},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"301","医生":"蒋**","拜访类型":"正式拜访","时长分钟":40},
    {"代表":"张三","月份":"2026-07","药名":"克罗凯","医院":"301","医生":"沈**","拜访类型":"正式拜访","时长分钟":35},
    {"代表":"张三","月份":"2026-06","药名":"维我单抗","医院":"北大人民","医生":"黄晓军","拜访类型":"学术拜访","时长分钟":60},
    {"代表":"张三","月份":"2026-07","药名":"维我单抗","医院":"北大人民","医生":"黄晓军","拜访类型":"正式拜访","时长分钟":65},
]

VALID_FIELDS = ["代表","月份","药名","医院","医生","拜访类型","时长分钟"]


def _filter_records(filters):
    result = []
    for r in RECORDS:
        ok = True
        for k, v in filters.items():
            if not v:
                continue
            if k == "month_start":
                if r["月份"] < v:
                    ok = False
            elif k == "month_end":
                if r["月份"] > v:
                    ok = False
            else:
                if k in VALID_FIELDS and r.get(k) != v:
                    ok = False
        if ok:
            result.append(r)
    return result


def _stat_group(result, group_by, agg):
    stats = {}
    for r in result:
        key = r.get(group_by, "未知")
        if key not in stats:
            stats[key] = {"count": 0, "hospitals": set(), "duration": 0}
        stats[key]["count"] += 1
        stats[key]["hospitals"].add(r["医院"])
        stats[key]["duration"] += r["时长分钟"]

    lines = []
    for k in sorted(stats.keys()):
        s = stats[k]
        parts = [f"{k}"]
        if "count" in agg:
            parts.append(f"次数:{s['count']}")
        if "distinct(医院)" in agg:
            parts.append(f"医院数:{len(s['hospitals'])}")
        if "sum(时长)" in agg:
            parts.append(f"总时长:{s['duration']}分钟")
        lines.append("|".join(parts))
    return "\n".join(lines), len(result)


def _list_field(result, list_field):
    values = sorted(set(r.get(list_field, "") for r in result))
    return "、".join(values), len(values)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body_raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            body = json.loads(body_raw) if body_raw else {}
        except Exception:
            body = {}

        filters = body.get("filters", {}) or {}
        query_type = body.get("query_type", "stat")
        group_by = body.get("group_by")
        agg = body.get("agg", ["count", "distinct(医院)", "sum(时长)"])
        list_field = body.get("list_field")

        result = _filter_records(filters)

        if query_type == "list":
            summary, total = _list_field(result, list_field or "医院")
        else:
            summary, total = _stat_group(result, group_by or "月份", agg)

        out = {
            "summary_text": summary,
            "total": total,
            "query_type": query_type,
        }
        resp = json.dumps(out, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass
