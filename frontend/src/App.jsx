import { useEffect, useState, useRef } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hi! 👋 I'm the Company Assistant. How can I help you?",
    },
  ]);

  const [menu, setMenu] = useState([]);
  const [input, setInput] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [contactLoading, setContactLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Fetch suggested questions

  useEffect(() => {
    fetch(`${API_URL}/menu`)
      .then((response) => response.json())
      .then((data) => {
        setMenu(data);
      })
      .catch((error) => {
        console.error("Failed to load menu:", error);
      });
  }, []);

  // Auto-scroll to latest message

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Send chat message

  const sendMessage = async (question) => {
    if (!question.trim() || loading) return;

    // Add USER message first
    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: question,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      console.log("Chatbot response:", data);

      // Add BOT response
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: data.answer,

          // Important for contact flow
          needsContact: data.needs_contact || false,

          // Keep original question
          question: question,

          // Useful for debugging
          intent: data.intent,
          confidence: data.confidence,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------
  // Submit chat input
  // --------------------------------

  const handleSubmit = (event) => {
    event.preventDefault();

    sendMessage(input);
  };

  // Submit contact request

  const submitContact = async (question) => {
    if (!email.trim()) {
      alert("Please enter your email address.");
      return;
    }

    setContactLoading(true);

    try {
      const response = await fetch(`${API_URL}/contact`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          question: question,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to submit contact request");
      }

      const data = await response.json();

      // Add confirmation message
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            data.message || "Thanks! Our team will get back to you shortly.",
        },
      ]);

      setEmail("");
    } catch (error) {
      console.error("Contact error:", error);

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Sorry, we couldn't submit your request. Please try again.",
        },
      ]);
    } finally {
      setContactLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        {/* Header */}

        <div className="chat-header">
          <div className="chat-header-avatar">🤖</div>

          <div className="chat-header-text">
            <h1>Company Assistant</h1>
            <div className="status">
              <span className="status-dot"></span>
              Online
            </div>
          </div>
        </div>

        {/* Messages */}

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message-row ${message.sender}`}>
              <div className="message-content">
                <div className="message">{message.text}</div>

                {/* Contact form */}

                {message.sender === "bot" && message.needsContact && (
                  <div className="contact-form">
                    <input
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(event) => setEmail(event.target.value)}
                      disabled={contactLoading}
                    />

                    <button
                      onClick={() => submitContact(message.question)}
                      disabled={contactLoading}
                    >
                      {contactLoading ? "Sending..." : "Contact Team"}
                    </button>
                  </div>
                )}

                {/* Development information */}

                {message.sender === "bot" && message.intent && (
                  <div className="debug-info">
                    Intent: {message.intent}
                    {message.confidence !== undefined &&
                      ` • Confidence: ${message.confidence}`}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Typing indicator */}

          {loading && (
            <div className="message-row bot">
              <div className="message-content">
                <div className="message typing-bubble">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions */}

        {messages.length === 1 && (
          <div className="suggestions">
            <p>Try asking</p>

            <div className="suggestion-list">
              {menu.slice(0, 6).map((item) => (
                <button
                  key={item.question_id}
                  onClick={() => sendMessage(item.question)}
                >
                  {item.question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}

        <form className="chat-input" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Ask something..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={loading}
          />

          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;