import ReactMarkdown from "react-markdown";
import { useState } from "react";
import "./App.css";



function extractSources(answer) {
  const uniquePages = new Set();

  const citationRegex =
    /\[Source\s+\d+,\s*Pages?\s+\d+(?:\s*;\s*Source\s+\d+,\s*Pages?\s+\d+)*\]|\[Pages?\s+\d+(?:\s*,\s*(?:Pages?\s+)?\d+)*\]/gi;

  const citations = [...answer.matchAll(citationRegex)];

  for (const citation of citations) {
    const pageMatches = citation[0].match(
      /Page\s+(\d+)/gi
    ) || [];

    pageMatches.forEach((page) => {
      const number = page.match(/\d+/);
      if (number) {
        uniquePages.add(Number(number[0]));
      }
    });

    // Also support compact formats such as [Pages 22, 154].
    const compactMatch = citation[0].match(
      /^\[Pages?\s+([\d,\s]+)\]$/i
    );

    if (compactMatch) {
      compactMatch[1].split(",").forEach((page) => {
        const number = Number(page.trim());
        if (Number.isFinite(number)) {
          uniquePages.add(number);
        }
      });
    }
  }

  const cleanAnswer = answer
    .replace(citationRegex, "")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  return {
    cleanAnswer,
    sources: [...uniquePages].sort((a, b) => a - b),
  };
}




const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [documentId, setDocumentId] = useState("");
  const [documentName, setDocumentName] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");
  const [showSources, setShowSources] = useState(false);

  async function uploadPdf(event) {
    event.preventDefault();

    if (!file) {
      setError("Please select a PDF first.");
      return;
    }

    setUploading(true);
    setError("");
    setAnswer("");
    setDocumentId("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/documents`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "PDF upload failed.");
      }

      setDocumentId(data.document_id);
      setDocumentName(data.filename);
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    } finally {
      setUploading(false);
    }
  }

  async function askQuestion(event) {
    event.preventDefault();

    if (!documentId || !question.trim()) return;

    setAsking(true);
    setError("");
    setAnswer("");

    try {
      const response = await fetch(
        `${API_URL}/api/documents/${documentId}/questions`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: question.trim() }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not generate an answer.");
      }

      setAnswer(data.answer);
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-mark">FR</div>
        <div>
          <h1>Financial Research Copilot</h1>
          <p>Research your financial documents with AI</p>
        </div>
        <span className="local-badge">LOCAL MVP</span>
      </header>

      <section className="hero">
        <span className="eyebrow">DOCUMENT INTELLIGENCE</span>
        <h2>Your financial reports, easier to understand.</h2>
        <p>
          Upload a PDF annual report, ask a question, and get an answer
          grounded in the document with page references.
        </p>
      </section>

      <section className="workspace">
        <div className="panel upload-panel">
          <div className="section-heading">
            <span className="step-number">01</span>
            <div>
              <h3>Upload a document</h3>
              <p>Select a financial report in PDF format.</p>
            </div>
          </div>

          <form onSubmit={uploadPdf}>
            <label className="file-picker">
              <span className="upload-icon">↑</span>
              <strong>{file ? file.name : "Choose a PDF file"}</strong>
              <span>PDF files only · Maximum 25 MB</span>
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={(event) => {
                  setFile(event.target.files?.[0] || null);
                  setError("");
                }}
              />
            </label>

            <button className="primary-button" disabled={uploading}>
              {uploading ? "Processing document..." : "Upload and process"}
            </button>
          </form>

          {uploading && (
            <p className="helper-text">
              Extracting text and creating the search index. Large PDFs may
              take a minute or more. Please keep this page open.
            </p>
          )}

          {documentId && (
            <div className="document-success">
              <span className="success-dot" />
              <div>
                <strong>Document ready</strong>
                <p>{documentName}</p>
                <small>Your PDF is indexed and ready for questions.</small>
              </div>
            </div>
          )}
        </div>

        <div className="panel question-panel">
          <div className="section-heading">
            <span className="step-number">02</span>
            <div>
              <h3>Ask your report</h3>
              <p>Ask a specific question about the uploaded document.</p>
            </div>
          </div>

          <form onSubmit={askQuestion}>
            <label className="field-label" htmlFor="question">
              Your question
            </label>
            <textarea
              id="question"
              rows="4"
              placeholder={
                documentId
                  ? "What was the consolidated revenue in FY 2024-25?"
                  : "Upload a PDF first to start asking questions."
              }
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              disabled={!documentId || asking}
            />

            <button
              className="primary-button"
              disabled={!documentId || !question.trim() || asking}
            >
              {asking ? "Researching document..." : "Generate answer"}
            </button>
          </form>

          {!documentId && (
            <p className="helper-text">
              Your question box will become available after a successful
              upload.
            </p>
          )}
        </div>
      </section>

      {error && (
        <section className="message error-message" role="alert">
          <strong>Something went wrong</strong>
          <p>{error}</p>
        </section>
      )}

      
{answer && (() => {
  const { cleanAnswer, sources } = extractSources(answer);

  return (
    <section className="panel answer-panel">
      <div className="section-heading">
        <div>
          <h3>Research answer</h3>
          <p>Generated using your uploaded document.</p>
        </div>
      </div>

      <div className="answer-content">
        <ReactMarkdown>{cleanAnswer}</ReactMarkdown>
      </div>

      {sources.length > 0 && (
        <div className="sources-section">
          <button
            type="button"
            className="sources-toggle"
            onClick={() => setShowSources((previous) => !previous)}
            aria-expanded={showSources}
          >
            <span>Sources ({sources.length})</span>
            <span>{showSources ? "−" : "+"}</span>
          </button>

          {showSources && (
            <ul className="sources-list">
              {sources.map((page) => (
                <li key={page}>Page {page}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  );
})()}


      <footer>
        Financial Research Copilot · Local development build
      </footer>
    </main>
  );
}

export default App;
