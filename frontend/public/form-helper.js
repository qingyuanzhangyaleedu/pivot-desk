/* Runs only after an explicit extension click. Never submits or accepts agreements. */
(() => {
  const norm = (v) =>
    String(v || "")
      .toLowerCase()
      .replace(/[^a-z0-9 ]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  const manual =
    /consent|agree|terms|privacy|signature|certif|acknowledge|disability|gender|race|ethnic|birth|social security|ssn|password/;
  function label(el) {
    return (
      [...(el.labels || [])].map((x) => x.innerText).join(" ") ||
      el.getAttribute("aria-label") ||
      el.getAttribute("data-automation-id") ||
      el.placeholder ||
      el.name ||
      el.id
    );
  }
  function fields() {
    return [...document.querySelectorAll("input,textarea,select")].filter(
      (e) =>
        e.getClientRects().length &&
        !e.disabled &&
        !e.readOnly &&
        !["hidden", "password", "file", "submit", "button", "reset"].includes(
          e.type,
        ),
    );
  }
  function valueFor(el, packet) {
    const name = norm(label(el));
    const allowed = new Set([
      "full_name",
      "email",
      "phone",
      "linkedin",
      "location",
      "experience.title",
      "experience.organization",
      "experience.description",
      "education.title",
      "education.organization",
      "language",
    ]);
    const explicit = allowed.has(el.dataset.pivotKey)
      ? el.dataset.pivotKey
      : null;
    const facts = packet.facts || [];
    const section = el.closest(
      '[data-experience-index],fieldset,[data-automation-id="workExperience"],[data-automation-id="educationSection"]',
    );
    let index = Number(section?.dataset.experienceIndex || 0);
    if (
      !section?.dataset.experienceIndex &&
      section?.getAttribute("data-automation-id") === "workExperience"
    )
      index = [
        ...document.querySelectorAll('[data-automation-id="workExperience"]'),
      ].indexOf(section);
    const experience = facts.filter((f) => f.kind === "experience")[index];
    const education = facts.find((f) => f.kind === "education");
    if (manual.test(name) || ["checkbox", "radio"].includes(el.type))
      return [null, "Read and answer this on the employer page."];
    if (/veteran/.test(name))
      return [
        packet.veteran_status || null,
        "Sensitive answer: requires your explicit profile choice.",
      ];
    if (/authoriz|sponsor/.test(name))
      return [
        /sponsor/.test(name) ? null : packet.work_authorization || null,
        "Do not infer eligibility or sponsorship.",
      ];
    const key =
      explicit ||
      (/first name|given name/.test(name)
        ? "first_name"
        : /last name|family name/.test(name)
          ? "last_name"
          : /full name|legal name/.test(name)
            ? "full_name"
            : /email/.test(name)
              ? "email"
              : /phone|mobile/.test(name)
                ? "phone"
                : /linkedin/.test(name)
                  ? "linkedin"
                  : /job title|position title/.test(name)
                    ? "experience.title"
                    : /company|employer/.test(name)
                      ? "experience.organization"
                      : /role description|responsibil|job description/.test(
                            name,
                          )
                        ? "experience.description"
                        : /school|university|institution/.test(name)
                          ? "education.organization"
                          : /degree/.test(name)
                            ? "education.title"
                            : /language/.test(name)
                              ? "language"
                              : /location|city/.test(name) && !section
                                ? "location"
                                : null);
    if (!key) return [null, "No reliable field mapping; enter manually."];
    if (key === "first_name" || key === "last_name")
      return [
        null,
        "Names are not split automatically. Use the full-name field or enter each part yourself.",
      ];
    if (key.startsWith("experience."))
      return [
        experience?.[key.split(".")[1]] || null,
        "Reviewed work-history entry " + (index + 1),
      ];
    if (key.startsWith("education."))
      return [
        education?.[key.split(".")[1]] || null,
        "Reviewed education entry",
      ];
    if (key === "language")
      return [
        facts.find((f) => f.kind === "language")?.title || null,
        "Only an explicitly stated language",
      ];
    if (/start|end/.test(key))
      return [null, "Confirm employer-specific date format manually."];
    return [packet[key] || null, "From your reviewed profile"];
  }
  function preview(packet) {
    if (packet?.format !== "pivot-profile-v1")
      throw Error("Import a Pivot Desk profile packet first.");
    return fields().map((el, index) => {
      const [raw, why] = valueFor(el, packet);
      let value = raw,
        reason = why;
      if (value && el.tagName === "SELECT") {
        const option = [...el.options].find(
          (o) => norm(o.text) === norm(value) || norm(o.value) === norm(value),
        );
        value = option?.value || null;
        if (!value) reason = "No exact option match; choose manually.";
      }
      if (value && el.value && el.value !== value) {
        value = null;
        reason = "Existing answer protected; edit it yourself.";
      }
      if (
        value &&
        el.type === "email" &&
        !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)
      ) {
        value = null;
        reason = "Check the email format.";
      }
      return {
        index,
        label: label(el),
        value,
        reason,
        current: el.value || "",
        sensitive: /veteran|authoriz|sponsor/.test(norm(label(el))),
        key: el.id + "|" + el.name + "|" + label(el),
      };
    });
  }
  function apply(packet, approved) {
    const plan = preview(packet),
      elements = fields();
    let filled = 0;
    const skipped = [];
    for (const choice of approved) {
      const row = plan.find(
        (x) =>
          x.index === choice.index &&
          x.key === choice.key &&
          x.value === choice.value,
      );
      if (!row?.value) {
        skipped.push(choice.label);
        continue;
      }
      const el = elements[row.index];
      const proto =
        el.tagName === "SELECT"
          ? HTMLSelectElement.prototype
          : el.tagName === "TEXTAREA"
            ? HTMLTextAreaElement.prototype
            : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, "value").set.call(el, row.value);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      filled++;
    }
    return { filled, skipped, submitted: false, agreements_accepted: false };
  }
  window.PivotFill = { preview, apply };
})();
