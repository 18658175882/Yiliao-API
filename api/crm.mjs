const RECORDS = [
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
];

const VALID_FIELDS = ["代表","月份","药名","医院","医生","拜访类型","时长分钟"];

function filterRecords(filters) {
    return RECORDS.filter((r) => {
        for (const [k, v] of Object.entries(filters)) {
            if (!v) continue;
            if (k === "month_start") {
                if (r["月份"] < v) return false;
            } else if (k === "month_end") {
                if (r["月份"] > v) return false;
            } else {
                if (VALID_FIELDS.includes(k) && r[k] !== v) return false;
            }
        }
        return true;
    });
}

function statGroup(result, groupBy, agg) {
    const stats = {};
    for (const r of result) {
        const key = r[groupBy] || "未知";
        if (!stats[key]) stats[key] = { count: 0, hospitals: new Set(), duration: 0 };
        stats[key].count += 1;
        stats[key].hospitals.add(r["医院"]);
        stats[key].duration += r["时长分钟"];
    }
    const lines = [];
    for (const k of Object.keys(stats).sort()) {
        const s = stats[k];
        const parts = [k];
        if (agg.includes("count")) parts.push(`次数:${s.count}`);
        if (agg.includes("distinct(医院)")) parts.push(`医院数:${s.hospitals.size}`);
        if (agg.includes("sum(时长)")) parts.push(`总时长:${s.duration}分钟`);
        lines.push(parts.join("|"));
    }
    return { summary: lines.join("\n"), total: result.length };
}

function listField(result, field) {
    const values = [...new Set(result.map((r) => r[field] || ""))].sort();
    return { summary: values.join("、"), total: values.length };
}

export default function handler(req, res) {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    if (req.method === "OPTIONS") {
        res.status(204).end();
        return;
    }
    if (req.method !== "POST") {
        res.status(405).json({ error: "Method not allowed" });
        return;
    }

    let body = {};
    try {
        body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    } catch (e) {
        body = {};
    }

    const filters = body.filters || {};
    const queryType = body.query_type || "stat";
    const groupBy = body.group_by || "月份";
    const agg = body.agg || ["count", "distinct(医院)", "sum(时长)"];
    const listFieldName = body.list_field || "医院";

    const result = filterRecords(filters);

    let summary, total;
    if (queryType === "list") {
        ({ summary, total } = listField(result, listFieldName));
    } else {
        ({ summary, total } = statGroup(result, groupBy, agg));
    }

    res.status(200).json({
        summary_text: summary,
        total: total,
        query_type: queryType,
    });
}
