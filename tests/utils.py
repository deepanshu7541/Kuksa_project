def read_vss_value(client, path):
    if hasattr(client, "get_current_values"):
        res = client.get_current_values([path])
    elif hasattr(client, "get_values"):
        res = client.get_values([path])
    else:
        res = client.get([path])

    if isinstance(res, dict) and path in res:
        item = res[path]
        if hasattr(item, "value"):
            return item.value
        if isinstance(item, dict) and "value" in item:
            return item["value"]

    if isinstance(res, dict) and "results" in res:
        for r in res["results"]:
            if isinstance(r, dict) and r.get("path") == path:
                return r.get("value") if "value" in r else getattr(r, "value", None)

    raise AssertionError(f"Unexpected response shape for {path}: {res!r}")
