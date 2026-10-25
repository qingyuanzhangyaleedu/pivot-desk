let packet = null,
  plan = [],
  tabId = null;
const $ = (id) => document.getElementById(id),
  say = (s) => ($("status").textContent = s);
chrome.storage.session.get("packet").then((x) => {
  packet = x.packet || null;
  if (packet) say("A profile is loaded for this browser session.");
});
$("file").onchange = async (e) => {
  try {
    packet = JSON.parse(await e.target.files[0].text());
    if (packet.format !== "pivot-profile-v1")
      throw Error("Wrong packet format");
    await chrome.storage.session.set({ packet });
    say("Profile imported. Preview the current application page.");
  } catch (e) {
    packet = null;
    say(e.message);
  }
};
$("preview").onclick = async () => {
  try {
    if (!packet) throw Error("Import your reviewed profile packet.");
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    tabId = tab.id;
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ["content.js"],
    });
    const [r] = await chrome.scripting.executeScript({
      target: { tabId },
      func: (p) => window.PivotFill.preview(p),
      args: [packet],
    });
    plan = r.result;
    $("plan").replaceChildren();
    for (const row of plan) {
      const div = document.createElement("div");
      div.className = "row";
      const label = document.createElement("label");
      const check = document.createElement("input");
      check.type = "checkbox";
      check.disabled = !row.value;
      check.checked = !!row.value && !row.sensitive;
      check.dataset.index = row.index;
      label.append(check, document.createTextNode(" " + row.label));
      const text = document.createElement("small");
      text.textContent = row.value || row.reason;
      div.append(label, text);
      $("plan").append(div);
    }
    say(
      plan.filter((x) => x.value).length +
        " fields available. Check sensitive answers individually.",
    );
  } catch (e) {
    say(e.message);
  }
};
$("review").onchange = () => {
  $("fill").disabled = !$("review").checked;
};
$("fill").onclick = async () => {
  try {
    if (!$("review").checked) throw Error("Review first");
    const selected = plan.filter(
      (r) => $("plan").querySelector(`input[data-index="${r.index}"]`)?.checked,
    );
    const [r] = await chrome.scripting.executeScript({
      target: { tabId },
      func: (p, a) => window.PivotFill.apply(p, a),
      args: [packet, selected],
    });
    say(
      `${r.result.filled} fields filled. Review the form; nothing was submitted.`,
    );
    $("review").checked = false;
    $("fill").disabled = true;
  } catch (e) {
    say(e.message);
  }
};
$("clear").onclick = async () => {
  packet = null;
  plan = [];
  await chrome.storage.session.remove("packet");
  $("plan").replaceChildren();
  say("Profile removed from extension session storage.");
};
