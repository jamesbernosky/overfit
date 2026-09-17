const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

async function readBody(req) {
  if (req.body && typeof req.body === "object") {
    return req.body;
  }

  if (typeof req.body === "string") {
    return JSON.parse(req.body);
  }

  const chunks = [];

  for await (const chunk of req) {
    chunks.push(chunk);
  }

  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
}

module.exports = async function subscribe(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed." });
  }

  const apiKey = process.env.BUTTONDOWN_API_KEY;

  if (!apiKey) {
    return res.status(500).json({ error: "Newsletter is not configured yet." });
  }

  let body;

  try {
    body = await readBody(req);
  } catch {
    return res.status(400).json({ error: "Invalid request body." });
  }

  const email = String(body.email || "").trim().toLowerCase();

  if (!EMAIL_PATTERN.test(email)) {
    return res.status(400).json({ error: "Enter a valid email address." });
  }

  const forwardedFor = req.headers["x-forwarded-for"];
  const ipAddress = Array.isArray(forwardedFor)
    ? forwardedFor[0]
    : String(forwardedFor || "").split(",")[0].trim();

  const response = await fetch("https://api.buttondown.com/v1/subscribers", {
    method: "POST",
    headers: {
      "Authorization": `Token ${apiKey}`,
      "Content-Type": "application/json",
      "X-Buttondown-Collision-Behavior": "add"
    },
    body: JSON.stringify({
      email_address: email,
      ip_address: ipAddress || undefined
    })
  });

  if (!response.ok) {
    let details = {};

    try {
      details = await response.json();
    } catch {
      details = {};
    }

    return res.status(response.status).json({
      error: details.detail || details.email_address?.[0] || "Could not subscribe this email."
    });
  }

  return res.status(200).json({
    message: "Check your email to confirm."
  });
};
