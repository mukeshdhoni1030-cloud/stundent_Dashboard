
import { useEffect, useState } from "react";
import api from "./services/api";
import "./App.css";

import TeacherDashboard from "./components/TeacherDashboard";
import PrincipalDashboard from "./components/PrincipalDashboard";
import StudentDashboard from "./components/StudentDashboard";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [cooldownSeconds, setCooldownSeconds] = useState(0);

  const [token, setToken] = useState(
    sessionStorage.getItem("access_token")
  );

  const [role, setRole] = useState(
    sessionStorage.getItem("user_role")
  );

  // Countdown after rate limit
  useEffect(() => {
    if (cooldownSeconds <= 0) return;

    const timer = setTimeout(() => {
      setCooldownSeconds((seconds) => seconds - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [cooldownSeconds]);

  async function handleLogin(event) {
    event.preventDefault();

    if (cooldownSeconds > 0 || loading) return;

    setError("");

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    try {
      setLoading(true);

      const response = await api.post("/auth/login", {
        email,
        password,
      });

      const accessToken = response.data.access_token;
      const userRole = response.data.role?.toLowerCase();

      if (!accessToken || !userRole) {
        setError("Invalid login response from server.");
        return;
      }

      if (!["teacher", "principal", "student"].includes(userRole)) {
        setError("Your account does not have dashboard access.");
        return;
      }

      sessionStorage.setItem("access_token", accessToken);
      sessionStorage.setItem("user_role", userRole);

      setToken(accessToken);
      setRole(userRole);
      setPassword("");
    } catch (err) {
      if (err.response?.status === 429) {
        setCooldownSeconds(60);
        setError(
          "Too many login attempts. Please wait before trying again."
        );
      } else {
        setError(
          err.response?.data?.detail ||
            "Login failed. Please check your credentials."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("user_role");

    setToken(null);
    setRole(null);

    setEmail("");
    setPassword("");
    setError("");
    setCooldownSeconds(0);
  }

  if (!token || !role) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-logo">SD</div>

          <p className="login-eyebrow">
            SCHOOL MANAGEMENT SYSTEM
          </p>

          <h1>Welcome Back</h1>

          <p className="login-description">
            Sign in to access your school dashboard.
          </p>

          <form onSubmit={handleLogin}>
            <div className="login-field">
              <label htmlFor="login-email">Email Address</label>
              <input
                id="login-email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                disabled={cooldownSeconds > 0}
                required
              />
            </div>

            <div className="login-field">
              <label htmlFor="login-password">Password</label>
              <input
                id="login-password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={cooldownSeconds > 0}
                required
              />
            </div>

            {error && (
              <div
                className={
                  cooldownSeconds > 0
                    ? "login-error login-rate-limit"
                    : "login-error"
                }
              >
                {error}

                {cooldownSeconds > 0 && (
                  <p className="login-countdown">
                    Try again in {cooldownSeconds} seconds.
                  </p>
                )}
              </div>
            )}

            <button
              className="login-button"
              type="submit"
              disabled={loading || cooldownSeconds > 0}
            >
              {loading
                ? "Signing in..."
                : cooldownSeconds > 0
                ? `Wait ${cooldownSeconds}s`
                : "Login"}
            </button>
          </form>

          <p className="login-footer">
            Secure School Dashboard Access
          </p>
        </div>
      </div>
    );
  }

  if (role === "teacher") {
    return (
      <>
        <div className="dashboard-topbar">
          <span>Teacher Portal</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
        <TeacherDashboard />
      </>
    );
  }

  if (role === "principal") {
    return (
      <>
        <div className="dashboard-topbar">
          <span>Principal Portal</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
        <PrincipalDashboard />
      </>
    );
  }

  if (role === "student") {
    return (
      <>
        <div className="dashboard-topbar">
          <span>Student Portal</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
        <StudentDashboard />
      </>
    );
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h2>Invalid user role</h2>
        <button onClick={handleLogout}>Back to Login</button>
      </div>
    </div>
  );
}

export default App;
