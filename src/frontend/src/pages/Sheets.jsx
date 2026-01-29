import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function Sheets() {
  const [sheets, setSheets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newSheetName, setNewSheetName] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadSheets();
  }, []);

  const loadSheets = async () => {
    try {
      const data = await api.getSheets();
      setSheets(data);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSheet = async (e) => {
    e.preventDefault();
    if (!newSheetName.trim()) return;

    setCreating(true);
    setError(null);

    try {
      const sheet = await api.createSheet({ name: newSheetName });
      setSheets([sheet, ...sheets]);
      setNewSheetName("");
    } catch (err) {
      setError(err);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSheet = async (sheetId) => {
    if (!confirm("Remove this checklist?")) return;

    try {
      await api.deleteSheet(sheetId);
      setSheets(sheets.filter((s) => s.id !== sheetId));
    } catch (err) {
      setError(err);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h3 className="mb-4">My Checklists</h3>

      {error && (
        <div className="alert alert-danger py-2 d-flex justify-content-between align-items-center">
          <span>
            {error.getUserFriendlyMessage?.() ||
              error.message ||
              "An error occurred"}
          </span>
          {error.isRetryable?.() && (
            <button
              className="btn btn-sm btn-outline-danger"
              onClick={loadSheets}
            >
              Retry
            </button>
          )}
        </div>
      )}

      <form onSubmit={handleCreateSheet} className="mb-4">
        <div className="row g-2">
          <div className="col">
            <input
              type="text"
              className="form-control"
              placeholder="New checklist name"
              value={newSheetName}
              onChange={(e) => setNewSheetName(e.target.value)}
            />
          </div>
          <div className="col-auto">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={creating}
            >
              {creating ? "Creating..." : "Create"}
            </button>
          </div>
        </div>
      </form>

      {sheets.length === 0 ? (
        <p className="text-muted">No checklists yet.</p>
      ) : (
        <table className="table table-hover">
          <thead>
            <tr>
              <th>Name</th>
              <th style={{ width: 100 }}></th>
            </tr>
          </thead>
          <tbody>
            {sheets.map((sheet) => (
              <tr key={sheet.id}>
                <td>
                  <Link to={`/sheets/${sheet.id}/`}>{sheet.name}</Link>
                </td>
                <td>
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDeleteSheet(sheet.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
