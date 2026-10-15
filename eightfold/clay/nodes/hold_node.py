def handler(context):
    return {"status": "Review", "reason": "identity unresolved: " + (context.get_input("identity_reason") or "")}
