const API_BASE = "http://127.0.0.1:8000/api";

async function handle(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
  return data;
}

export function initRequest(idNumber, firstName) {
  return fetch(`${API_BASE}/requests/init`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idNumber, firstName }),
  }).then(handle);
}

export function confirmRequest(requestId) {
  return fetch(`${API_BASE}/requests/${requestId}/confirm`, {
    method: "POST",
  }).then(handle);
}

export function manualVerify(requestId, mpesaReceipt) {
  return fetch(`${API_BASE}/payments/manual-verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ requestId, mpesaReceipt }),
  }).then(handle);
}

export function getResult(requestId) {
  return fetch(`${API_BASE}/requests/${requestId}/result`).then(handle);
}

/** STK push (stub for now) */
export function stkPush(requestId, phone) {
  return fetch(`${API_BASE}/payments/stk-push`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ requestId, phone }),
  }).then(handle);
}

/** Poll payment status */
export function getPaymentStatus(requestId) {
  return fetch(`${API_BASE}/payments/status/${requestId}`).then(handle);
}

/** DEV ONLY: simulate callback paid */
export function simulatePaid(requestId) {
  return fetch(`${API_BASE}/payments/simulate-paid/${requestId}`, {
    method: "POST",
  }).then(handle);
}
