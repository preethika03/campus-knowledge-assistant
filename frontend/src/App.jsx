import { useEffect, useState } from "react";
import "./App.css";
import AdminPanel from "./AdminPanel";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [user, setUser] = useState(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  const [error, setError] = useState("");

  const [adminPanelOpen, setAdminPanelOpen] = useState(false);

  // =====================================================
  // CHECK EXISTING LOGIN
  // =====================================================

  useEffect(() => {
    const savedToken = localStorage.getItem("access_token");
    const savedUser = localStorage.getItem("user");

    if (savedToken && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
      }
    }
  }, []);

  // =====================================================
  // CHECK ADMIN ROLE
  // =====================================================

  const isAdmin = user && Number(user.role_id) === 4;

  // =====================================================
  // LOAD CHAT HISTORY
  // =====================================================

  useEffect(() => {
    if (user) {
      loadHistory();
    }
  }, [user]);

  const loadHistory = async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      return;
    }

    setHistoryLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/chat/history`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        handleLogout();
        return;
      }

      if (!response.ok || !data.success) {
        return;
      }

      setHistory(data.history || []);

    } catch (err) {
      console.error(
        "Could not load chat history:",
        err
      );
    } finally {
      setHistoryLoading(false);
    }
  };

  // =====================================================
  // LOGIN
  // =====================================================

  const handleLogin = async (event) => {
    event.preventDefault();

    setLoginLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        setError(
          data.message || "Login failed."
        );
        return;
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      localStorage.setItem(
        "user",
        JSON.stringify(data.user)
      );

      setUser(data.user);

      setEmail("");
      setPassword("");
      setError("");

    } catch (err) {
      setError(
        "Could not connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoginLoading(false);
    }
  };

  // =====================================================
  // LOGOUT
  // =====================================================

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setUser(null);
    setQuestion("");
    setAnswer("");
    setSources([]);
    setHistory([]);
    setError("");
    setAdminPanelOpen(false);
  };

  // =====================================================
  // ASK QUESTION
  // =====================================================

  const handleAskQuestion = async (event) => {
    event.preventDefault();

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
      setError(
        "Your session has expired. Please log in again."
      );

      handleLogout();
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(
        `${API_URL}/chat/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            question: question.trim(),
          }),
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );

        handleLogout();
        return;
      }

      if (!response.ok || !data.success) {
        setError(
          data.detail ||
          data.message ||
          "Unable to generate an answer."
        );

        return;
      }

      setAnswer(data.answer || "");
      setSources(data.sources || []);

      await loadHistory();

    } catch (err) {
      setError(
        "Could not connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // OPEN HISTORY ITEM
  // =====================================================

  const openHistoryItem = (item) => {
    setQuestion(item.question || "");
    setAnswer(item.answer || "");
    setSources(item.sources || []);
    setError("");
    setAdminPanelOpen(false);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // =====================================================
  // NEW CHAT
  // =====================================================

  const startNewChat = () => {
    setQuestion("");
    setAnswer("");
    setSources([]);
    setError("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // =====================================================
  // OPEN ADMIN PANEL
  // =====================================================

  const openAdminPanel = () => {
    setAdminPanelOpen(true);
    setError("");
  };

  // =====================================================
  // CLOSE ADMIN PANEL
  // =====================================================

  const closeAdminPanel = () => {
    setAdminPanelOpen(false);
  };

  // =====================================================
  // RENDER CLICKABLE CITATIONS
  // =====================================================

  const renderAnswer = (text) => {
    if (!text) {
      return null;
    }

    const parts = text.split(
      /(\[Source \d+\])/g
    );

    return parts.map((part, index) => {
      const match = part.match(
        /^\[Source (\d+)\]$/
      );

      if (match) {
        const sourceNumber =
          Number(match[1]);

        const sourceExists =
          sourceNumber >= 1 &&
          sourceNumber <= sources.length;

        if (sourceExists) {
          return (
            <a
              key={index}
              href={`#source-${sourceNumber}`}
              className="inline-citation"
            >
              {part}
            </a>
          );
        }
      }

      return (
        <span key={index}>
          {part}
        </span>
      );
    });
  };

  // =====================================================
  // FORMAT DATE
  // =====================================================

  const formatDate = (dateValue) => {
    if (!dateValue) {
      return "";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
      return "";
    }

    return date.toLocaleString(
      undefined,
      {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      }
    );
  };

  // =====================================================
  // LOGIN PAGE
  // =====================================================

  if (!user) {
    return (
      <div className="app">

        <div className="login-container">

          <div className="login-info">

            <div className="logo-circle">
              📚
            </div>

            <h1>
              Campus Knowledge
              <span>Assistant</span>
            </h1>

            <p className="subtitle">
              Your intelligent university knowledge
              companion.
            </p>

            <div className="feature-list">

              <div className="feature">

                <div className="feature-icon">
                  🔎
                </div>

                <div>
                  <h3>
                    Smart Search
                  </h3>

                  <p>
                    Find information from university
                    documents using semantic search.
                  </p>
                </div>

              </div>


              <div className="feature">

                <div className="feature-icon">
                  🔐
                </div>

                <div>
                  <h3>
                    Secure Access
                  </h3>

                  <p>
                    Information is filtered according
                    to your permissions and role.
                  </p>
                </div>

              </div>


              <div className="feature">

                <div className="feature-icon">
                  ✨
                </div>

                <div>
                  <h3>
                    AI-Powered Answers
                  </h3>

                  <p>
                    Get clear answers with references
                    to the original documents.
                  </p>
                </div>

              </div>

            </div>

          </div>


          <div className="login-card">

            <div className="card-header">

              <p className="welcome">
                WELCOME BACK
              </p>

              <h2>
                Sign in to your account
              </h2>

              <p>
                Access your campus knowledge assistant.
              </p>

            </div>


            <form onSubmit={handleLogin}>

              <div className="form-group">

                <label htmlFor="email">
                  Email
                </label>

                <input
                  id="email"
                  type="email"
                  placeholder="Enter your university email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  required
                />

              </div>


              <div className="form-group">

                <label htmlFor="password">
                  Password
                </label>

                <input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  required
                />

              </div>


              <button
                type="submit"
                className="login-button"
                disabled={loginLoading}
              >
                {loginLoading
                  ? "Signing in..."
                  : "Sign In"}
              </button>

            </form>


            {error && (
              <div className="message error">
                {error}
              </div>
            )}


            <div className="security-note">
              🔒 Your account is protected by
              role-based authentication.
            </div>

          </div>

        </div>


        <div className="footer">
          Campus Knowledge Assistant · AI-powered
          university information system
        </div>

      </div>
    );
  }


  // =====================================================
  // CHAT DASHBOARD
  // =====================================================

  return (
    <div className="dashboard">

      <header className="dashboard-header">

        <div className="brand">

          <div className="brand-icon">
            📚
          </div>

          <div>

            <h1>
              Campus Knowledge Assistant
            </h1>

            <p>
              AI-powered university knowledge system
            </p>

          </div>

        </div>


        <div className="user-section">

          <div className="user-info">

            <strong>
              {user.name}
            </strong>

            <span>
              {user.email}
            </span>

          </div>


          {isAdmin && (
            <button
              className="admin-header-button"
              onClick={openAdminPanel}
            >
              ⚙️ Admin
            </button>
          )}


          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>


      <div className="dashboard-layout">

        {/* =================================================
            HISTORY SIDEBAR
        ================================================= */}

        <aside className="history-sidebar">

          <div className="history-header">

            <div>

              <h3>
                Recent Chats
              </h3>

              <span>
                {history.length} conversation
                {history.length === 1
                  ? ""
                  : "s"}
              </span>

            </div>


            <button
              className="new-chat-button"
              onClick={startNewChat}
            >
              + New
            </button>

          </div>


          <div className="history-list">

            {historyLoading && (
              <div className="history-loading">
                Loading history...
              </div>
            )}


            {!historyLoading &&
              history.length === 0 && (

                <div className="history-empty">

                  <div className="history-empty-icon">
                    💬
                  </div>

                  <p>
                    Your previous questions
                    will appear here.
                  </p>

                </div>

              )}


            {!historyLoading &&
              history.map((item) => (

                <button
                  key={item.id}
                  className="history-item"
                  onClick={() =>
                    openHistoryItem(item)
                  }
                >

                  <div className="history-question">
                    {item.question}
                  </div>

                  <div className="history-date">
                    {formatDate(
                      item.created_at
                    )}
                  </div>

                </button>

              ))}

          </div>

        </aside>


        {/* =================================================
            MAIN CONTENT
        ================================================= */}

        <main className="dashboard-main">

          <div className="welcome-area">

            <p className="dashboard-label">
              CAMPUS AI ASSISTANT
            </p>

            <h2>
              Hello, {user.name.split(" ")[0]} 👋
            </h2>

            <p>
              Ask questions about university policies,
              attendance, examinations, leave, library
              rules, and other campus documents.
            </p>

          </div>


          {/* QUESTION BOX */}

          <div className="chat-card">

            <form onSubmit={handleAskQuestion}>

              <label htmlFor="question">
                What would you like to know?
              </label>

              <textarea
                id="question"
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                placeholder="Ask something about your campus..."
                rows="5"
              />

              <div className="question-footer">

                <span>
                  Answers are generated from authorized
                  campus documents.
                </span>

                <button
                  type="submit"
                  className="ask-button"
                  disabled={loading}
                >
                  {loading
                    ? "Thinking..."
                    : "Ask Assistant"}
                </button>

              </div>

            </form>

          </div>


          {/* ERROR */}

          {error && (
            <div className="dashboard-error">
              {error}
            </div>
          )}


          {/* ANSWER */}

          {answer && (

            <div className="answer-card">

              <div className="section-heading">

                <div className="section-icon">
                  ✨
                </div>

                <div>

                  <h3>
                    AI Answer
                  </h3>

                  <p>
                    Generated from authorized documents
                  </p>

                </div>

              </div>


              <div className="answer-content">
                {renderAnswer(answer)}
              </div>

            </div>

          )}


          {/* SOURCES */}

          {sources.length > 0 && (

            <div className="sources-card">

              <div className="section-heading">

                <div className="section-icon">
                  📖
                </div>

                <div>

                  <h3>
                    Sources
                  </h3>

                  <p>
                    Documents used to generate this answer
                  </p>

                </div>

              </div>


              <div className="sources-list">

                {sources.map((source, index) => (

                  <div
                    className="source-item"
                    id={`source-${index + 1}`}
                    key={`${source.chunk_id}-${index}`}
                  >

                    <div className="source-number">
                      {index + 1}
                    </div>

                    <div className="source-details">

                      <strong>
                        {source.filename}
                      </strong>

                      <span>
                        {source.title}
                      </span>

                      <small>
                        Document {source.document_id}
                        {" · "}
                        Chunk {source.chunk_index}
                      </small>

                    </div>

                  </div>

                ))}

              </div>

            </div>

          )}


          {/* EMPTY STATE */}

          {!answer &&
            !loading &&
            !error && (

              <div className="empty-state">

                <div className="empty-icon">
                  💬
                </div>

                <h3>
                  Ask your first question
                </h3>

                <p>
                  Try asking:
                </p>

                <button
                  className="example-question"
                  onClick={() =>
                    setQuestion(
                      "What are the attendance requirements?"
                    )
                  }
                >
                  What are the attendance requirements?
                </button>

              </div>

            )}

        </main>

      </div>


      <footer className="dashboard-footer">
        Campus Knowledge Assistant ·
        Secure AI-powered campus information
      </footer>


      {/* =================================================
          ADMIN PANEL
      ================================================= */}

      {adminPanelOpen && isAdmin && (
        <AdminPanel
          onClose={closeAdminPanel}
        />
      )}

    </div>
  );
}

export default App;