import React, { useState } from "react";

export default function ChecklistItem({
  item,
  depth = 0,
  busyRowId,
  disabled,
  onUpdate,
  onDelete,
  onIndent,
  onOutdent,
  onMoveUp,
  onMoveDown,
}) {
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: item.name,
    status: item.status,
    assignee: item.assignee,
    notes: item.notes,
  });

  const isBusy = busyRowId === item.id;

  const handleSave = () => {
    onUpdate(item.id, editData);
    setEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      name: item.name,
      status: item.status,
      assignee: item.assignee,
      notes: item.notes,
    });
    setEditing(false);
  };

  const statusColor = {
    "Not Started": "#6c757d",
    "In Progress": "#ffc107",
    Complete: "#198754",
  };

  return (
    <div>
      <div
        className={`py-2 pe-2 border-bottom d-flex align-items-center${
          isBusy ? " bg-light" : ""
        }`}
        style={{
          paddingLeft: `${12 + depth * 24}px`,
          opacity: isBusy ? 0.6 : 1,
        }}
      >
        {editing ? (
          <div className="flex-grow-1">
            <div className="row g-2 mb-2">
              <div className="col-4">
                <input
                  type="text"
                  className="form-control form-control-sm"
                  value={editData.name}
                  onChange={(e) =>
                    setEditData({ ...editData, name: e.target.value })
                  }
                />
              </div>
              <div className="col-2">
                <select
                  className="form-select form-select-sm"
                  value={editData.status}
                  onChange={(e) =>
                    setEditData({ ...editData, status: e.target.value })
                  }
                >
                  <option>Not Started</option>
                  <option>In Progress</option>
                  <option>Complete</option>
                </select>
              </div>
              <div className="col-2">
                <input
                  type="text"
                  className="form-control form-control-sm"
                  value={editData.assignee}
                  onChange={(e) =>
                    setEditData({ ...editData, assignee: e.target.value })
                  }
                  placeholder="Assignee"
                />
              </div>
              <div className="col-2">
                <input
                  type="text"
                  className="form-control form-control-sm"
                  value={editData.notes}
                  onChange={(e) =>
                    setEditData({ ...editData, notes: e.target.value })
                  }
                  placeholder="Notes"
                />
              </div>
              <div className="col-2">
                <button
                  className="btn btn-sm btn-success me-1"
                  onClick={handleSave}
                  disabled={disabled}
                >
                  Save
                </button>
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={handleCancel}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        ) : (
          <>
            <div className="flex-grow-1">
              {isBusy && (
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                ></span>
              )}
              <span className="me-2">{item.name}</span>
              <span
                className="badge"
                style={{
                  backgroundColor: statusColor[item.status] || "#6c757d",
                }}
              >
                {item.status}
              </span>
              {item.assignee && (
                <span className="text-muted small ms-2">({item.assignee})</span>
              )}
              {item.notes && (
                <span className="text-muted small ms-2">- {item.notes}</span>
              )}
            </div>
            <div className="btn-group btn-group-sm">
              <button
                className="btn btn-outline-secondary"
                onClick={() => onMoveUp(item.id)}
                disabled={disabled}
                title="Move up"
              >
                <i className="fa-solid fa-arrow-up"></i>
              </button>
              <button
                className="btn btn-outline-secondary"
                onClick={() => onMoveDown(item.id)}
                disabled={disabled}
                title="Move down"
              >
                <i className="fa-solid fa-arrow-down"></i>
              </button>
              <button
                className="btn btn-outline-secondary"
                onClick={() => onOutdent(item.id)}
                disabled={disabled}
                title="Outdent"
              >
                <i className="fa-solid fa-outdent"></i>
              </button>
              <button
                className="btn btn-outline-secondary"
                onClick={() => onIndent(item.id)}
                disabled={disabled}
                title="Indent"
              >
                <i className="fa-solid fa-indent"></i>
              </button>
              <button
                className="btn btn-outline-secondary"
                onClick={() => setEditing(true)}
                disabled={disabled}
                title="Edit"
              >
                <i className="fa-solid fa-pen"></i>
              </button>
              <button
                className="btn btn-outline-danger"
                onClick={() => onDelete(item.id)}
                disabled={disabled}
                title="Delete"
              >
                <i className="fa-solid fa-trash"></i>
              </button>
            </div>
          </>
        )}
      </div>

      {item.children &&
        item.children.map((child) => (
          <ChecklistItem
            key={child.id}
            item={child}
            depth={depth + 1}
            busyRowId={busyRowId}
            disabled={disabled}
            onUpdate={onUpdate}
            onDelete={onDelete}
            onIndent={onIndent}
            onOutdent={onOutdent}
            onMoveUp={onMoveUp}
            onMoveDown={onMoveDown}
          />
        ))}
    </div>
  );
}
