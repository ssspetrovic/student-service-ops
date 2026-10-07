import http from "k6/http";
import { check, sleep } from "k6";
import { Counter, Rate, Trend } from "k6/metrics";

let baseUrl = __ENV.LOAD_TEST_BASE_URL || "https://student-service.internal";
if (baseUrl.endsWith("/")) baseUrl = baseUrl.slice(0, -1);
const email = __ENV.LOAD_TEST_EMAIL;
const password = __ENV.LOAD_TEST_PASSWORD;
const phase = __ENV.LOAD_TEST_PHASE || "measured";
let defaultVus = 10;
let defaultDurationSeconds = 180;
if (phase === "smoke") defaultVus = 1;
if (phase !== "measured") defaultDurationSeconds = 30;
const vus = Number(__ENV.LOAD_TEST_VUS || defaultVus);
const durationSeconds = Number(__ENV.LOAD_TEST_DURATION_SECONDS || defaultDurationSeconds);
const duration = durationSeconds + "s";
const pause = Number(__ENV.LOAD_TEST_PAUSE_SECONDS || 1);

if (!email || !password) throw new Error("Set LOAD_TEST_EMAIL and LOAD_TEST_PASSWORD");

if (!Number.isInteger(vus) || vus < 1 || !Number.isFinite(durationSeconds) || durationSeconds <= 0) {
  throw new Error("Use a positive whole VU count and a positive duration in seconds");
}

let minimumSamples = 100;
if (phase !== "measured") minimumSamples = 1;
let successThreshold = "rate>0.99";
let failureThreshold = "rate<0.01";
if (phase === "smoke") {
  successThreshold = "rate==1";
  failureThreshold = "rate==0";
}

const metrics = {};
for (const name of ["login", "identity", "profile", "enrollments", "exams", "wallet", "transactions"]) {
  metrics[name] = {
    duration: new Trend(name + "_duration", true),
    failures: new Rate(name + "_failures"),
    checks: new Rate(name + "_checks"),
    requests: new Counter(name + "_requests"),
  };
}

const thresholds = {
  login_failures: ["rate==0"],
  login_checks: ["rate==1"],
  login_requests: ["count==1"],
  identity_failures: ["rate==0"],
  identity_checks: ["rate==1"],
  identity_requests: ["count==1"],
};

for (const name of ["profile", "enrollments", "exams", "wallet", "transactions"]) {
  thresholds[name + "_duration"] = ["p(95)<1000"];
  thresholds[name + "_failures"] = [failureThreshold];
  thresholds[name + "_checks"] = [successThreshold];
  thresholds[name + "_requests"] = ["count>=" + minimumSamples];
}

const scenarios = {
  student: {
    exec: "testStudent",
    executor: "constant-vus",
    vus,
    duration,
    gracefulStop: "10s",
  },
};

export const options = {
  scenarios,
  thresholds,
  summaryTrendStats: ["med", "p(95)", "p(99)", "max"],
};

function readJson(response) {
  try {
    return response.json();
  } catch {
    return null;
  }
}

function record(response, name, validData) {
  const endpoint = metrics[name];
  endpoint.requests.add(1);
  endpoint.duration.add(response.timings.duration);
  endpoint.failures.add(response.status !== 200);
  const succeeded = check(response, {
    [`${name}: HTTP 200 and expected data`]: function (result) {
      return result.status === 200 && validData;
    },
  });
  endpoint.checks.add(succeeded);
  return succeeded;
}

function get(path, name, accessToken) {
  return http.get(`${baseUrl}${path}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    tags: { name },
    redirects: 0,
    timeout: "10s",
  });
}

export function setup() {
  console.log(`Preparing student session: ${new Date().toISOString()}`);
  const response = http.post(
    `${baseUrl}/api/auth/token/`,
    JSON.stringify({ email, password }),
    {
      headers: { "Content-Type": "application/json" },
      tags: { name: "login" },
      redirects: 0,
      timeout: "10s",
    },
  );
  const data = readJson(response);
  const validTokens = data !== null && Boolean(data.access) && Boolean(data.refresh);
  if (!record(response, "login", validTokens)) {
    throw new Error("Session setup failed: login did not return HTTP 200 with both tokens");
  }

  const userResponse = get("/api/accounts/me/", "identity", data.access);
  const user = readJson(userResponse);
  const validUser = user !== null && user.email === email && user.role === "student";
  if (!record(userResponse, "identity", validUser)) {
    throw new Error("Session setup failed: expected student identity was not verified");
  }
  console.log(`Session ready; ${durationSeconds}s of student activity will start after setup.`);
  return { access: data.access, refresh: data.refresh };
}

export function testStudent(session) {
  let response = get("/api/accounts/student-profile/", "profile", session.access);
  let data = readJson(response);
  record(response, "profile", data !== null && data.email === email && data.role === "student");
  sleep(pause);

  response = get("/api/academics/enrollments/", "enrollments", session.access);
  record(response, "enrollments", Array.isArray(readJson(response)));
  sleep(pause);

  response = get("/api/exams/available/", "exams", session.access);
  record(response, "exams", Array.isArray(readJson(response)));
  sleep(pause);

  response = get("/api/finance/wallet/", "wallet", session.access);
  data = readJson(response);
  const validWallet = data !== null
    && data.balance !== undefined && data.balance !== null
    && data.student_index_no !== undefined && data.student_index_no !== null;
  record(response, "wallet", validWallet);
  response = get("/api/finance/transactions/", "transactions", session.access);
  record(response, "transactions", Array.isArray(readJson(response)));
  sleep(pause);
}

export function teardown() {
  console.log(`HTTP load ended (including up to 10s grace): ${new Date().toISOString()}`);
}
