ANGLES = {
    "Economic buyer (CHRO / CPO)": (
        "skills baseline for the first-90-days people strategy",
        "Most new people leaders I talk to owe their CEO a workforce plan in the first quarter, and the hard part is knowing "
        "which skills you already have before deciding what to hire, reskill or redeploy."),
    "Operational owner (Head / VP of TA)": (
        "recruiter capacity on high-volume hiring",
        "With {roles} roles posted in the last 30 days, the fastest capacity gain is usually rediscovering qualified people "
        "already sitting in {ats} before sourcing net-new."),
    "Talent intelligence / people analytics": (
        "a skills dataset for workforce planning",
        "A new talent intelligence function lives or dies on the dataset: one skills view of the workforce, benchmarked "
        "against the external market, that planning and TA can both trust."),
    "HR technology (CIO / HRIT)": (
        "AI on top of the existing HCM, not a replacement",
        "Eightfold runs on top of {ats} rather than replacing it, and TalentForge lets your team build its own talent "
        "agents with the governance IT needs."),
}


def handler(context):
    g = lambda k: "" if context.get_input(k) is None else str(context.get_input(k)).strip()
    persona = g("persona_group") or "Operational owner (Head / VP of TA)"
    installs = context.get_input("installs") or []
    systems = []
    for i in installs:
        n = i.get("product_name") or ""
        if n and n not in systems:
            systems.append(n)
    ats = ", ".join(systems[:2]) or "your current HCM and ATS"
    roles_raw = context.get_input("job_count")
    roles = "{:,}".format(int(roles_raw)) if roles_raw is not None else "your"
    angle, hook = ANGLES.get(persona, ANGLES["Operational owner (Head / VP of TA)"])
    hook = hook.format(roles=roles, ats=ats)
    email = g("work_email")
    valid = g("email_validation")
    first = g("first_name") or "there"
    company = g("company")
    subject = "%s, %s at %s" % (first, angle, company)
    body = ("Hi %s,\n\nCongrats on the new role as %s at %s.\n\n%s\n\n"
            "Eightfold maps the skills of every employee and applicant so you can hire, move and develop people against "
            "the same picture. Open to a 20-minute look at what that baseline would show for %s?\n\n[Rep name]") % (
        first, g("title"), company, hook, company)
    slack = ("*New talent leader at %s* (%s)\n"
             "*Who:* %s, %s (started %s) %s\n"
             "*Email:* %s%s\n"
             "*Context:* %s open roles in 30 days; HR stack: %s\n"
             "*Angle:* %s\n"
             "*Suggested subject:* %s") % (
        company, persona, g("full_name"), g("title"), g("start_date") or "recently", g("profile_url"),
        email or "not found", (" (%s)" % valid) if valid else "", roles, ", ".join(systems) or "not detected", angle, subject)
    return {"slack_message": slack, "email_to": email, "email_validation": valid or "not found",
            "email_subject": subject, "email_body": body, "angle": angle}
