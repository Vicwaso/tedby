import { useMemo, useState } from "react";
import "./App.css";
import {
  initRequest,
  confirmRequest,
  manualVerify,
  getResult,
  stkPush,
  getPaymentStatus,
  simulatePaid,
} from "./api";

export default function App() {
  const [step, setStep] = useState("INIT"); // INIT -> CONFIRM -> PAY -> RESULT
  const [idNumber, setIdNumber] = useState("");
  const [firstName, setFirstName] = useState("");
  const [requestId, setRequestId] = useState(null);
  const [maskedName, setMaskedName] = useState("");

  // Payment state
  const [payMethod, setPayMethod] = useState("STK"); // STK | MANUAL
  const [phone, setPhone] = useState("");
  const [stkMsg, setStkMsg] = useState("");
  const [receipt, setReceipt] = useState("");

  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const currentStepIndex = useMemo(() => {
    const order = ["INIT", "CONFIRM", "PAY", "RESULT"];
    return order.indexOf(step);
  }, [step]);

  const canContinueInit = idNumber.trim().length >= 6 && firstName.trim().length >= 2;

  function resetAll() {
    setErr("");
    setStep("INIT");
    setIdNumber("");
    setFirstName("");
    setRequestId(null);
    setMaskedName("");
    setPayMethod("STK");
    setPhone("");
    setStkMsg("");
    setReceipt("");
    setResult(null);
    setLoading(false);
  }

  async function onInit(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const data = await initRequest(idNumber.trim(), firstName.trim());
      setRequestId(data.requestId);
      setMaskedName(data.maskedName);
      setStep("CONFIRM");
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  }

  async function onConfirmYes() {
    setErr("");
    setLoading(true);
    try {
      await confirmRequest(requestId);
      setStep("PAY");
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  }

  async function onPayManual(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      await manualVerify(requestId, receipt.trim());
      const res = await getResult(requestId);
      setResult(res);
      setStep("RESULT");
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  }

  async function onCheckPayment() {
    setErr("");
    setLoading(true);
    try {
      const s = await getPaymentStatus(requestId);

      if (s.status === "PAID" || s.status === "RELEASED") {
        const res = await getResult(requestId);
        setResult(res);
        setStep("RESULT");
        return;
      }

      setStkMsg(`Current status: ${s.status}. If you already paid, wait a bit then check again.`);
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  }

  async function pollUntilPaid(maxTries = 10) {
    for (let i = 0; i < maxTries; i++) {
      const s = await getPaymentStatus(requestId);
      if (s.status === "PAID" || s.status === "RELEASED") {
        const res = await getResult(requestId);
        setResult(res);
        setStep("RESULT");
        return true;
      }
      await new Promise((r) => setTimeout(r, 2500));
    }
    return false;
  }

  async function onSendStk() {
    setErr("");
    setStkMsg("");
    setLoading(true);
    try {
      const data = await stkPush(requestId, phone.trim());
      setStkMsg(data.message || "STK prompt requested. Check your phone.");
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }

    // Auto poll (non-blocking feel)
    const ok = await pollUntilPaid(10);
    if (!ok) setStkMsg("Still pending. If you paid, click “I have paid — Check status”.");
  }

  async function onDevSimulatePaid() {
    setErr("");
    setLoading(true);
    try {
      await simulatePaid(requestId);
      await onCheckPayment();
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="wrap">
      <div className="card">
        <div className="header">
          <div className="brand">
            <div className="logo" />
            <div>
              <h1 className="h1">TEDBY PIN Checker</h1>
              <p className="sub">Find your KRA PIN using your ID number. Fast • Secure • Mobile-friendly</p>
            </div>
          </div>
        </div>

        <div className="body">
          <div className="steps">
            <div className={`pill ${currentStepIndex >= 0 ? "on" : ""}`}>1. Details</div>
            <div className={`pill ${currentStepIndex >= 1 ? "on" : ""}`}>2. Confirm</div>
            <div className={`pill ${currentStepIndex >= 2 ? "on" : ""}`}>3. Pay</div>
            <div className={`pill ${currentStepIndex >= 3 ? "on" : ""}`}>4. Result</div>
          </div>

          {err && <div className="alert">{err}</div>}

          {step === "INIT" && (
            <form onSubmit={onInit} className="grid">
              <div>
                <label>ID Number</label>
                <input
                  className="input"
                  value={idNumber}
                  onChange={(e) => setIdNumber(e.target.value.replace(/\s/g, ""))}
                  inputMode="numeric"
                  placeholder="e.g. 41293742"
                />
                <div className="hint">Enter your National ID number (numbers only).</div>
              </div>

              <div>
                <label>First Name</label>
                <input
                  className="input"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="e.g. Otieno"
                />
                <div className="hint">We use it to verify it matches your KRA record.</div>
              </div>

              <div className="btnRow">
                <button className="btn btnPrimary" disabled={!canContinueInit || loading}>
                  {loading ? "Checking..." : "Continue"}
                </button>
              </div>

              <div className="footer">
                Tip: Use the name exactly as it appears on your official record (spelling matters).
              </div>
            </form>
          )}

          {step === "CONFIRM" && (
            <div>
              <div className="hint">Please confirm this matches your name.</div>
              <div className="bigName">{maskedName}</div>

              <div className="btnRow">
                <button className="btn btnPrimary" onClick={onConfirmYes} disabled={loading}>
                  {loading ? "Saving..." : "Yes, that’s me"}
                </button>
              </div>

              <div className="btnRow">
                <button className="btn" onClick={() => setStep("INIT")} disabled={loading}>
                  No, go back
                </button>
              </div>

              <div className="footer">We only show a masked name to protect your privacy.</div>
            </div>
          )}

          {step === "PAY" && (
            <div className="grid">
              <div className="kpi">
                <p className="kpiTitle">Payment</p>
                <p style={{ margin: 0, color: "var(--text)" }}>
                  Amount: <b>KES 100</b> • Till: <b>8993804</b>
                </p>
                <p className="hint" style={{ marginTop: 8 }}>
                  Choose STK Prompt (recommended) or Manual Code (fallback).
                </p>
              </div>

              <div style={{ display: "flex", gap: 10 }}>
                <button
                  type="button"
                  className={`btn ${payMethod === "STK" ? "btnPrimary" : ""}`}
                  onClick={() => setPayMethod("STK")}
                  disabled={loading}
                >
                  STK Prompt
                </button>
                <button
                  type="button"
                  className={`btn ${payMethod === "MANUAL" ? "btnPrimary" : ""}`}
                  onClick={() => setPayMethod("MANUAL")}
                  disabled={loading}
                >
                  Manual Code
                </button>
              </div>

              {payMethod === "STK" && (
                <div className="grid">
                  <div>
                    <label>Phone Number</label>
                    <input
                      className="input"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value.replace(/\s/g, ""))}
                      placeholder="07XXXXXXXX or 2547XXXXXXXX"
                      inputMode="tel"
                    />
                    <div className="hint">We’ll send an STK prompt to this number.</div>
                  </div>

                  {stkMsg && (
                    <div className="kpi">
                      <div className="hint">{stkMsg}</div>
                    </div>
                  )}

                  <div className="btnRow">
                    <button
                      type="button"
                      className="btn btnPrimary"
                      onClick={onSendStk}
                      disabled={loading || phone.trim().length < 10}
                    >
                      {loading ? "Sending..." : "Send STK Prompt"}
                    </button>
                  </div>

                  <div className="btnRow">
                    <button type="button" className="btn" onClick={onCheckPayment} disabled={loading}>
                      {loading ? "Checking..." : "I have paid — Check status"}
                    </button>
                  </div>

                  <div className="btnRow">
                    <button type="button" className="btn" onClick={onDevSimulatePaid} disabled={loading}>
                      Dev: Simulate Paid
                    </button>
                  </div>

                  <div className="footer">
                    If your phone prompt delays, confirm your number then try again.
                  </div>
                </div>
              )}

              {payMethod === "MANUAL" && (
                <form onSubmit={onPayManual} className="grid">
                  <div>
                    <label>M-PESA Transaction Code</label>
                    <input
                      className="input"
                      value={receipt}
                      onChange={(e) => setReceipt(e.target.value.toUpperCase().replace(/\s/g, ""))}
                      placeholder="e.g. RJ21D4NFLF"
                    />
                    <div className="hint">Fallback option if STK doesn’t work.</div>
                  </div>

                  <div className="btnRow">
                    <button className="btn btnPrimary" disabled={loading || receipt.trim().length < 8}>
                      {loading ? "Verifying..." : "Verify Payment"}
                    </button>
                  </div>
                </form>
              )}

              <div className="btnRow">
                <button type="button" className="btn" onClick={resetAll} disabled={loading}>
                  Start over
                </button>
              </div>
            </div>
          )}

          {step === "RESULT" && result && (
            <div>
              <div className="kpi">
                <p className="kpiTitle">Your KRA PIN</p>
                <p className="pin">{result.pin}</p>
              </div>

              <div style={{ marginTop: 12 }}>
                <div className="hint">
                  <b>Full Name:</b> {result.fullName}
                </div>
                <div className="hint">
                  <b>Email:</b> {result.generatedEmail}
                </div>

                <a
                  className="link"
                  href={`http://127.0.0.1:8000${result.certificateUrl}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Download Certificate PDF →
                </a>

                <div className="btnRow">
                  <button className="btn" onClick={resetAll}>
                    New Lookup
                  </button>
                </div>

                <div className="footer">Keep your PIN confidential. Do not share your certificate publicly.</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
