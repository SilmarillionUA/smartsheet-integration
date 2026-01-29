import React, { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import ChecklistItem from "../components/ChecklistItem";

function removeFromTree(items, rowId) {
  return items
    .filter((item) => item.id !== rowId)
    .map((item) => ({
      ...item,
      children: item.children ? removeFromTree(item.children, rowId) : [],
    }));
}

function updateInTree(items, rowId, data) {
  return items.map((item) => ({
    ...item,
    ...(item.id === rowId ? data : {}),
    children: item.children ? updateInTree(item.children, rowId, data) : [],
  }));
}

export default function Checklist() {
  const { sheetId } = useParams();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newItem, setNewItem] = useState({
    name: "",
    status: "Not Started",
    assignee: "",
    notes: "",
    parent_id: "",
  });
  const [busyRowId, setBusyRowId] = useState(null);
  const prevItems = useRef(null);

  const isBusy = busyRowId !== null;

  useEffect(() => {
    loadItems();
  }, [sheetId]);

  const loadItems = async () => {
    try {
      const data = await api.getItems(sheetId);
      setItems(data);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const withBusy = async (rowId, optimisticUpdate, apiCall) => {
    prevItems.current = items;
    if (optimisticUpdate) optimisticUpdate();

    await new Promise((r) => setTimeout(r, 0));

    setBusyRowId(rowId);
    setError(null);

    try {
      const result = await apiCall();
      if (result) setItems(result);
    } catch (err) {
      if (prevItems.current) setItems(prevItems.current);
      setError(err);
      if (!err.isRetryable?.()) {
        setTimeout(() => setError(null), 3000);
      }
    } finally {
      setBusyRowId(null);
      prevItems.current = null;
    }
  };

  const countItems = (items) => {
    let total = 0;
    let complete = 0;
    for (const item of items) {
      total++;
      if (item.status === "Complete") complete++;
      if (item.children?.length) {
        const child = countItems(item.children);
        total += child.total;
        complete += child.complete;
      }
    }
    return { total, complete };
  };

  const flattenItems = (items, depth = 0) => {
    let result = [];
    for (const item of items) {
      result.push({ ...item, depth });
      if (item.children?.length) {
        result = result.concat(flattenItems(item.children, depth + 1));
      }
    }
    return result;
  };

  const handleCreateItem = async (e) => {
    e.preventDefault();
    if (!newItem.name.trim()) return;

    const payload = { ...newItem, parent_id: newItem.parent_id || null };
    await withBusy("new", null, () => api.createItem(sheetId, payload));
    setNewItem({
      name: "",
      status: "Not Started",
      assignee: "",
      notes: "",
      parent_id: "",
    });
  };

  const handleUpdateItem = async (rowId, data) => {
    await withBusy(
      rowId,
      () => setItems((prev) => updateInTree(prev, rowId, data)),
      () => api.updateItem(sheetId, rowId, data),
    );
  };

  const handleDeleteItem = async (rowId) => {
    if (!confirm("Delete this item?")) return;

    await withBusy(
      rowId,
      () => setItems((prev) => removeFromTree(prev, rowId)),
      () => api.deleteItem(sheetId, rowId),
    );
  };

  const handleIndent = async (rowId) => {
    await withBusy(rowId, null, () => api.indentItem(sheetId, rowId));
  };

  const handleOutdent = async (rowId) => {
    await withBusy(rowId, null, () => api.outdentItem(sheetId, rowId));
  };

  const handleMoveUp = async (rowId) => {
    await withBusy(rowId, null, () => api.moveItemUp(sheetId, rowId));
  };

  const handleMoveDown = async (rowId) => {
    await withBusy(rowId, null, () => api.moveItemDown(sheetId, rowId));
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <div className="mb-4">
        <Link to="/sheets/">&larr; Back to lists</Link>
      </div>

      <h3 className="mb-3">Checklist Items</h3>

      {items.length > 0 &&
        (() => {
          const { total, complete } = countItems(items);
          const percent = Math.round((complete / total) * 100);
          return (
            <div className="mb-3">
              <div className="d-flex justify-content-between small mb-1">
                <span>
                  {complete} of {total} complete
                </span>
                <span>{percent}%</span>
              </div>
              <div className="progress" style={{ height: "8px" }}>
                <div
                  className="progress-bar bg-success"
                  role="progressbar"
                  style={{ width: `${percent}%` }}
                ></div>
              </div>
            </div>
          );
        })()}

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
              onClick={loadItems}
            >
              Retry
            </button>
          )}
        </div>
      )}

      <form
        onSubmit={handleCreateItem}
        className="mb-4 p-3 bg-light border rounded"
      >
        <div className="row g-2 align-items-end">
          <div className="col-md-3">
            <label className="form-label small">Task</label>
            <input
              type="text"
              className="form-control form-control-sm"
              value={newItem.name}
              onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
              required
            />
          </div>
          <div className="col-md-2">
            <label className="form-label small">Status</label>
            <select
              className="form-select form-select-sm"
              value={newItem.status}
              onChange={(e) =>
                setNewItem({ ...newItem, status: e.target.value })
              }
            >
              <option>Not Started</option>
              <option>In Progress</option>
              <option>Complete</option>
            </select>
          </div>
          <div className="col-md-2">
            <label className="form-label small">Parent</label>
            <select
              className="form-select form-select-sm"
              value={newItem.parent_id}
              onChange={(e) =>
                setNewItem({ ...newItem, parent_id: e.target.value })
              }
            >
              <option value="">None</option>
              {flattenItems(items).map((item) => (
                <option key={item.id} value={item.id}>
                  {"—".repeat(item.depth)} {item.name}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-2">
            <label className="form-label small">Assignee</label>
            <input
              type="text"
              className="form-control form-control-sm"
              value={newItem.assignee}
              onChange={(e) =>
                setNewItem({ ...newItem, assignee: e.target.value })
              }
            />
          </div>
          <div className="col-md-2">
            <label className="form-label small">Notes</label>
            <input
              type="text"
              className="form-control form-control-sm"
              value={newItem.notes}
              onChange={(e) =>
                setNewItem({ ...newItem, notes: e.target.value })
              }
            />
          </div>
          <div className="col-md-1">
            <button
              type="submit"
              className="btn btn-primary btn-sm w-100"
              disabled={isBusy}
            >
              {isBusy ? "..." : "Add"}
            </button>
          </div>
        </div>
      </form>

      {items.length === 0 ? (
        <p className="text-muted">No items yet.</p>
      ) : (
        <div className="border rounded">
          {items.map((item) => (
            <ChecklistItem
              key={item.id}
              item={item}
              busyRowId={busyRowId}
              disabled={isBusy}
              onUpdate={handleUpdateItem}
              onDelete={handleDeleteItem}
              onIndent={handleIndent}
              onOutdent={handleOutdent}
              onMoveUp={handleMoveUp}
              onMoveDown={handleMoveDown}
            />
          ))}
        </div>
      )}
    </div>
  );
}
