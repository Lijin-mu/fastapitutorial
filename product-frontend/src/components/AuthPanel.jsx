
import { useState } from "react";
import {
  getCurrentUser,
  loginUser,
  registerUser,
} from "../api/auth";

export default function AuthPanel({
  currentUser,
  onAuthenticated,
  onLogout,
}) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
      if (mode === "register") {
        await registerUser({ email, password });

        setMessage("Registration successful. You can now log in.");
        setMode("login");
        setPassword("");
        return;
      }

      const tokenData = await loginUser({ email, password });
      const user = await getCurrentUser(tokenData.access_token);

      onAuthenticated({
        token: tokenData.access_token,
        user,
      });

      setPassword("");
      setMessage("Login successful.");
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  if (currentUser) {
    return (
      <section className="auth-panel">
        <div>
          <h2>Welcome!</h2>
          <p>
            Signed in as <strong>{currentUser.email}</strong>
          </p>
        </div>

        <button
          type="button"
          className="auth-button secondary"
          onClick={onLogout}
        >
          Log out
        </button>
      </section>
    );
  }

  return (
    <section className="auth-panel">
      <h2>{mode === "login" ? "Log in" : "Create an account"}</h2>

      <p className="auth-description">
        {mode === "login"
          ? "Log in to access protected product actions."
          : "Register to create your account."}
      </p>

      <form onSubmit={handleSubmit} className="auth-form">
        <label htmlFor="auth-email">Email</label>
        <input
          id="auth-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          required
        />

        <label htmlFor="auth-password">Password</label>
        <input
          id="auth-password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete={
            mode === "login" ? "current-password" : "new-password"
          }
          minLength={8}
          maxLength={128}
          required
        />

        {error && <p className="auth-error" role="alert">{error}</p>}
        {message && <p className="auth-message" role="status">{message}</p>}

        <button
          type="submit"
          className="auth-button"
          disabled={loading}
        >
          {loading
            ? "Please wait..."
            : mode === "login"
              ? "Log in"
              : "Register"}
        </button>
      </form>

      <p className="auth-switch">
        {mode === "login"
          ? "Don't have an account?"
          : "Already have an account?"}{" "}
        <button
          type="button"
          className="text-button"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError("");
            setMessage("");
          }}
        >
          {mode === "login" ? "Register" : "Log in"}
        </button>
      </p>
    </section>
  );
}
