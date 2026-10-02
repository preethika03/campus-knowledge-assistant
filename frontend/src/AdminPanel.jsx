import { useEffect, useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

function AdminPanel({ onClose }) {
  // =====================================================
  // UPLOAD STATE
  // =====================================================

  const [file, setFile] = useState(null);

  const [uploading, setUploading] = useState(false);

  const [uploadResult, setUploadResult] = useState(null);

  const [uploadError, setUploadError] = useState("");


  // =====================================================
  // DOCUMENT LIST STATE
  // =====================================================

  const [documents, setDocuments] = useState([]);

  const [documentsLoading, setDocumentsLoading] = useState(false);

  const [documentsError, setDocumentsError] = useState("");

  const [statusLoadingId, setStatusLoadingId] = useState(null);

  const [statusError, setStatusError] = useState("");


  // =====================================================
  // USER LIST STATE
  // =====================================================

  const [users, setUsers] = useState([]);

  const [usersLoading, setUsersLoading] = useState(false);

  const [usersError, setUsersError] = useState("");

  const [userStatusLoadingId, setUserStatusLoadingId] =
    useState(null);

  const [userStatusError, setUserStatusError] =
    useState("");


  // =====================================================
  // PERMISSION STATE
  // =====================================================

  const [documentId, setDocumentId] = useState("");

  const [userId, setUserId] = useState("");

  const [canRead, setCanRead] = useState(true);

  const [permissionLoading, setPermissionLoading] =
    useState(false);

  const [permissionResult, setPermissionResult] =
    useState(null);

  const [permissionError, setPermissionError] =
    useState("");


  // =====================================================
  // LOAD DOCUMENTS + USERS
  // =====================================================

  useEffect(() => {
    loadDocuments();
    loadUsers();
  }, []);


  // =====================================================
  // LOAD DOCUMENTS
  // =====================================================

  const loadDocuments = async () => {
    const token =
      localStorage.getItem("access_token");

    if (!token) {
      setDocumentsError(
        "Your session has expired. Please log in again."
      );

      return;
    }

    setDocumentsLoading(true);
    setDocumentsError("");

    try {
      const response = await fetch(
        `${API_URL}/documents/`,
        {
          method: "GET",

          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        setDocumentsError(
          "You are not authorized. Please log in again."
        );

        return;
      }

      if (response.status === 403) {
        setDocumentsError(
          "You do not have permission to view documents."
        );

        return;
      }

      if (!response.ok || !data.success) {
        setDocumentsError(
          data.detail ||
          data.message ||
          "Could not load documents."
        );

        return;
      }

      setDocuments(data.documents || []);

    } catch (error) {
      setDocumentsError(
        "Could not connect to the backend."
      );

    } finally {
      setDocumentsLoading(false);
    }
  };


  // =====================================================
  // LOAD USERS
  // =====================================================

  const loadUsers = async () => {
    const token =
      localStorage.getItem("access_token");

    if (!token) {
      setUsersError(
        "Your session has expired. Please log in again."
      );

      return;
    }

    setUsersLoading(true);
    setUsersError("");

    try {
      const response = await fetch(
        `${API_URL}/admin/users`,
        {
          method: "GET",

          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        setUsersError(
          "You are not authorized. Please log in again."
        );

        return;
      }

      if (response.status === 403) {
        setUsersError(
          "Only administrators can view users."
        );

        return;
      }

      if (!response.ok || !data.success) {
        setUsersError(
          data.detail ||
          data.message ||
          "Could not load users."
        );

        return;
      }

      setUsers(data.users || []);

    } catch (error) {
      setUsersError(
        "Could not connect to the backend."
      );

    } finally {
      setUsersLoading(false);
    }
  };


  // =====================================================
  // UPDATE DOCUMENT STATUS
  // =====================================================

  const toggleDocumentStatus =
    async (document) => {

      const token =
        localStorage.getItem("access_token");

      if (!token) {
        setStatusError(
          "Your session has expired. Please log in again."
        );

        return;
      }

      const newStatus =
        !document.is_active;

      setStatusLoadingId(document.id);
      setStatusError("");

      try {
        const response = await fetch(
          `${API_URL}/documents/${document.id}/status` +
          `?is_active=${newStatus}`,
          {
            method: "PATCH",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();

        if (response.status === 401) {
          setStatusError(
            "You are not authorized. Please log in again."
          );

          return;
        }

        if (response.status === 403) {
          setStatusError(
            "Only administrators can change document status."
          );

          return;
        }

        if (!response.ok || !data.success) {
          setStatusError(
            data.detail ||
            data.message ||
            "Could not update document status."
          );

          return;
        }

        await loadDocuments();

      } catch (error) {
        setStatusError(
          "Could not connect to the backend."
        );

      } finally {
        setStatusLoadingId(null);
      }
    };


  // =====================================================
  // UPDATE USER STATUS
  // =====================================================

  const toggleUserStatus =
    async (user) => {

      const token =
        localStorage.getItem("access_token");

      if (!token) {
        setUserStatusError(
          "Your session has expired. Please log in again."
        );

        return;
      }

      const newStatus =
        !user.is_active;

      setUserStatusLoadingId(user.id);
      setUserStatusError("");

      try {
        const response = await fetch(
          `${API_URL}/admin/users/${user.id}/status` +
          `?is_active=${newStatus}`,
          {
            method: "PATCH",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();

        if (response.status === 401) {
          setUserStatusError(
            "You are not authorized. Please log in again."
          );

          return;
        }

        if (response.status === 403) {
          setUserStatusError(
            "Only administrators can change user status."
          );

          return;
        }

        if (!response.ok || !data.success) {
          setUserStatusError(
            data.detail ||
            data.message ||
            "Could not update user status."
          );

          return;
        }

        await loadUsers();

      } catch (error) {
        setUserStatusError(
          "Could not connect to the backend."
        );

      } finally {
        setUserStatusLoadingId(null);
      }
    };


  // =====================================================
  // UPLOAD PDF
  // =====================================================

  const handleUpload = async (event) => {
    event.preventDefault();

    if (!file) {
      setUploadError(
        "Please select a PDF file."
      );

      return;
    }

    if (
      !file.name
        .toLowerCase()
        .endsWith(".pdf")
    ) {
      setUploadError(
        "Only PDF files are allowed."
      );

      return;
    }

    const token =
      localStorage.getItem("access_token");

    if (!token) {
      setUploadError(
        "Your session has expired. Please log in again."
      );

      return;
    }

    setUploading(true);
    setUploadError("");
    setUploadResult(null);

    try {
      const formData =
        new FormData();

      formData.append(
        "file",
        file
      );

      const response =
        await fetch(
          `${API_URL}/documents/upload`,
          {
            method: "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },

            body: formData,
          }
        );

      const data = await response.json();

      if (response.status === 401) {
        setUploadError(
          "You are not authorized. Please log in again."
        );

        return;
      }

      if (response.status === 403) {
        setUploadError(
          "Only administrators can upload documents."
        );

        return;
      }

      if (!response.ok || !data.success) {
        setUploadError(
          data.detail ||
          data.message ||
          "Document upload failed."
        );

        return;
      }

      setUploadResult(data);

      setDocumentId(
        String(data.document_id)
      );

      setFile(null);

      await loadDocuments();

    } catch (error) {
      setUploadError(
        "Could not connect to the backend."
      );

    } finally {
      setUploading(false);
    }
  };


  // =====================================================
  // GRANT PERMISSION
  // =====================================================

  const handlePermission =
    async (event) => {

      event.preventDefault();

      if (!documentId) {
        setPermissionError(
          "Please select a document."
        );

        return;
      }

      if (!userId) {
        setPermissionError(
          "Please select a user."
        );

        return;
      }

      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!token) {
        setPermissionError(
          "Your session has expired. Please log in again."
        );

        return;
      }

      setPermissionLoading(true);
      setPermissionError("");
      setPermissionResult(null);

      try {
        const url =
          `${API_URL}/documents/${documentId}/permissions` +
          `?user_id=${encodeURIComponent(userId)}` +
          `&can_read=${canRead}`;

        const response =
          await fetch(
            url,
            {
              method: "POST",

              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          );

        const data =
          await response.json();

        if (response.status === 401) {
          setPermissionError(
            "You are not authorized. Please log in again."
          );

          return;
        }

        if (response.status === 403) {
          setPermissionError(
            "Only administrators can manage permissions."
          );

          return;
        }

        if (!response.ok || !data.success) {
          setPermissionError(
            data.detail ||
            data.message ||
            "Permission update failed."
          );

          return;
        }

        setPermissionResult(data);

      } catch (error) {
        setPermissionError(
          "Could not connect to the backend."
        );

      } finally {
        setPermissionLoading(false);
      }
    };


  // =====================================================
  // SELECT DOCUMENT
  // =====================================================

  const selectDocument = (id) => {
    setDocumentId(String(id));

    setPermissionResult(null);
    setPermissionError("");
  };


  // =====================================================
  // SELECT USER
  // =====================================================

  const selectUser = (id) => {
    setUserId(String(id));

    setPermissionResult(null);
    setPermissionError("");
  };


  // =====================================================
  // RETURN UI
  // =====================================================

  return (
    <div className="admin-overlay">

      <div className="admin-panel">

        {/* =================================================
            HEADER
        ================================================= */}

        <div className="admin-panel-header">

          <div>
            <p className="admin-label">
              ADMINISTRATION
            </p>

            <h2>
              Document Management
            </h2>

            <p>
              Upload campus documents and manage
              user access.
            </p>
          </div>

          <button
            className="admin-close-button"
            onClick={onClose}
          >
            ✕
          </button>

        </div>


        {/* =================================================
            CAMPUS DOCUMENTS
        ================================================= */}

        <section className="admin-section">

          <div className="admin-section-title">

            <div className="admin-section-icon">
              📚
            </div>

            <div>

              <h3>
                Campus Documents
              </h3>

              <p>
                View and manage all documents in the system.
              </p>

            </div>

          </div>


          <button
            type="button"
            className="admin-refresh-button"
            onClick={loadDocuments}
            disabled={documentsLoading}
          >
            {documentsLoading
              ? "Refreshing..."
              : "↻ Refresh Documents"}
          </button>


          {statusError && (
            <div className="admin-error">
              {statusError}
            </div>
          )}


          {documentsError && (
            <div className="admin-error">
              {documentsError}
            </div>
          )}


          {!documentsLoading &&
            !documentsError &&
            documents.length === 0 && (

              <div className="documents-empty">

                <div className="documents-empty-icon">
                  📂
                </div>

                <p>
                  No documents found.
                </p>

              </div>

            )}


          {documents.length > 0 && (

            <div className="documents-list">

              {documents.map(
                (document) => (

                  <div
                    className={
                      `document-item-wrapper ${
                        String(document.id) ===
                        String(documentId)
                          ? "document-item-wrapper-selected"
                          : ""
                      }`
                    }
                    key={document.id}
                  >

                    <button
                      type="button"
                      className="document-item"
                      onClick={() =>
                        selectDocument(
                          document.id
                        )
                      }
                    >

                      <div className="document-item-icon">
                        📄
                      </div>


                      <div className="document-item-content">

                        <strong>
                          {document.title}
                        </strong>

                        <span>
                          {document.filename}
                        </span>

                        <small>
                          Document ID:
                          {" "}
                          {document.id}
                          {" · "}
                          Uploaded by User:
                          {" "}
                          {document.uploaded_by}
                        </small>

                      </div>

                    </button>


                    <div className="document-status-area">

                      <span
                        className={
                          document.is_active
                            ? "document-status-active"
                            : "document-status-inactive"
                        }
                      >
                        {document.is_active
                          ? "Active"
                          : "Inactive"}
                      </span>


                      <button
                        type="button"
                        className={
                          document.is_active
                            ? "document-status-button deactivate"
                            : "document-status-button activate"
                        }
                        onClick={() =>
                          toggleDocumentStatus(
                            document
                          )
                        }
                        disabled={
                          statusLoadingId ===
                          document.id
                        }
                      >
                        {statusLoadingId ===
                        document.id
                          ? "Updating..."
                          : document.is_active
                            ? "Deactivate"
                            : "Activate"}
                      </button>

                    </div>

                  </div>

                )
              )}

            </div>

          )}

        </section>


        {/* =================================================
            USERS
        ================================================= */}

        <section className="admin-section">

          <div className="admin-section-title">

            <div className="admin-section-icon">
              👥
            </div>

            <div>

              <h3>
                Users
              </h3>

              <p>
                Select a user to manage account and
                document access.
              </p>

            </div>

          </div>


          <button
            type="button"
            className="admin-refresh-button"
            onClick={loadUsers}
            disabled={usersLoading}
          >
            {usersLoading
              ? "Refreshing..."
              : "↻ Refresh Users"}
          </button>


          {userStatusError && (
            <div className="admin-error">
              {userStatusError}
            </div>
          )}


          {usersError && (
            <div className="admin-error">
              {usersError}
            </div>
          )}


          {!usersLoading &&
            !usersError &&
            users.length === 0 && (

              <div className="documents-empty">

                <div className="documents-empty-icon">
                  👤
                </div>

                <p>
                  No users found.
                </p>

              </div>

            )}


          {users.length > 0 && (

            <div className="users-list">

              {users.map(
                (user) => (

                  <div
                    key={user.id}
                    className={
                      `user-item-wrapper ${
                        String(user.id) ===
                        String(userId)
                          ? "user-item-wrapper-selected"
                          : ""
                      }`
                    }
                  >

                    <button
                      type="button"
                      className="user-item"
                      onClick={() =>
                        selectUser(
                          user.id
                        )
                      }
                    >

                      <div className="user-item-icon">
                        👤
                      </div>


                      <div className="user-item-content">

                        <strong>
                          {user.name}
                        </strong>

                        <span>
                          {user.email}
                        </span>

                        <small>
                          User ID:
                          {" "}
                          {user.id}
                          {" · "}
                          Role:
                          {" "}
                          {user.role || "Unknown"}
                        </small>

                      </div>

                    </button>


                    <div className="user-status-area">

                      <span
                        className={
                          user.is_active
                            ? "user-status-active"
                            : "user-status-inactive"
                        }
                      >
                        {user.is_active
                          ? "Active"
                          : "Inactive"}
                      </span>


                      <button
                        type="button"
                        className={
                          user.is_active
                            ? "user-status-button deactivate"
                            : "user-status-button activate"
                        }
                        onClick={() =>
                          toggleUserStatus(
                            user
                          )
                        }
                        disabled={
                          userStatusLoadingId ===
                          user.id
                        }
                      >
                        {userStatusLoadingId ===
                        user.id
                          ? "Updating..."
                          : user.is_active
                            ? "Deactivate"
                            : "Activate"}
                      </button>

                    </div>

                  </div>

                )
              )}

            </div>

          )}

        </section>


        {/* =================================================
            UPLOAD DOCUMENT
        ================================================= */}

        <section className="admin-section">

          <div className="admin-section-title">

            <div className="admin-section-icon">
              📄
            </div>

            <div>

              <h3>
                Upload Document
              </h3>

              <p>
                Upload a university PDF for indexing.
              </p>

            </div>

          </div>


          <form onSubmit={handleUpload}>

            <label
              htmlFor="pdf-upload"
              className="file-drop-area"
            >

              <div className="upload-icon">
                ☁️
              </div>

              <strong>
                {file
                  ? file.name
                  : "Choose a PDF document"}
              </strong>

              <span>
                {file
                  ? "Selected file"
                  : "PDF files only"}
              </span>

              <input
                id="pdf-upload"
                type="file"
                accept=".pdf,application/pdf"
                onChange={(event) => {

                  const selected =
                    event.target.files?.[0] ||
                    null;

                  setFile(selected);
                  setUploadError("");
                  setUploadResult(null);

                }}
              />

            </label>


            <button
              type="submit"
              className="admin-primary-button"
              disabled={uploading}
            >
              {uploading
                ? "Uploading..."
                : "Upload PDF"}
            </button>

          </form>


          {uploadError && (
            <div className="admin-error">
              {uploadError}
            </div>
          )}


          {uploadResult && (

            <div className="admin-success">

              <strong>
                Document uploaded successfully 🎉
              </strong>

              <p>
                Document ID:
                {" "}
                <b>
                  {uploadResult.document_id}
                </b>
              </p>

              <p>
                Filename:
                {" "}
                {uploadResult.filename}
              </p>

              <p>
                Chunks created:
                {" "}
                {uploadResult.chunks_created}
              </p>

              {uploadResult.embeddings_created !==
                undefined && (

                <p>
                  Embeddings created:
                  {" "}
                  {uploadResult.embeddings_created}
                </p>

              )}

              <p>
                Text length:
                {" "}
                {uploadResult.text_length}
              </p>

            </div>

          )}

        </section>


        {/* =================================================
            DOCUMENT PERMISSIONS
        ================================================= */}

        <section className="admin-section">

          <div className="admin-section-title">

            <div className="admin-section-icon">
              🔐
            </div>

            <div>

              <h3>
                Document Permissions
              </h3>

              <p>
                Select a document and a user to manage access.
              </p>

            </div>

          </div>


          <form
            onSubmit={handlePermission}
            className="permission-form"
          >

            <div className="admin-form-group">

              <label htmlFor="document-id">
                Document ID
              </label>

              <input
                id="document-id"
                type="number"
                min="1"
                placeholder="Select a document above"
                value={documentId}
                onChange={(event) =>
                  setDocumentId(
                    event.target.value
                  )
                }
                required
              />

            </div>


            <div className="admin-form-group">

              <label htmlFor="user-id">
                User ID
              </label>

              <input
                id="user-id"
                type="number"
                min="1"
                placeholder="Select a user above"
                value={userId}
                onChange={(event) =>
                  setUserId(
                    event.target.value
                  )
                }
                required
              />

            </div>


            <label className="permission-checkbox">

              <input
                type="checkbox"
                checked={canRead}
                onChange={(event) =>
                  setCanRead(
                    event.target.checked
                  )
                }
              />

              <span>
                User can view this document
              </span>

            </label>


            <button
              type="submit"
              className="admin-primary-button"
              disabled={permissionLoading}
            >
              {permissionLoading
                ? "Updating..."
                : "Update Permission"}
            </button>

          </form>


          {permissionError && (
            <div className="admin-error">
              {permissionError}
            </div>
          )}


          {permissionResult && (

            <div className="admin-success">

              <strong>
                Permission updated successfully ✅
              </strong>

              <p>
                Document ID:
                {" "}
                {permissionResult.document_id}
              </p>

              <p>
                User ID:
                {" "}
                {permissionResult.user_id}
              </p>

              <p>
                Can view:
                {" "}
                {permissionResult.can_read
                  ? "Yes"
                  : "No"}
              </p>

            </div>

          )}

        </section>


        {/* =================================================
            WORKFLOW
        ================================================= */}

        <div className="admin-info-box">

          <strong>
            How document processing works
          </strong>

          <div className="admin-workflow">

            <span>
              PDF
            </span>

            <b>→</b>

            <span>
              Text Extraction
            </span>

            <b>→</b>

            <span>
              Chunking
            </span>

            <b>→</b>

            <span>
              Embeddings
            </span>

            <b>→</b>

            <span>
              Vector Search
            </span>

          </div>

        </div>

      </div>

    </div>
  );
}

export default AdminPanel;