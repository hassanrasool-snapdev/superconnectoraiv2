# Project Blueprint: Access Request Email Notifications

This document outlines the development plan for implementing an email notification system for the existing access request feature.

---

## Phase 1: High-Level Plan

### 1.1. Goal

The goal is to automate email notifications for access requests. When an administrator approves a request, the system will automatically send the requestor an email containing their temporary access passcode. When a request is denied, the system will send a polite decline notification. This eliminates the need for manual emailing by the administrator.

### 1.2. Architectural Approach

The implementation will leverage the existing backend email service. The new logic will be integrated directly into the current access request approval and denial workflows. The frontend will be updated with minor UI indicators to inform the admin that an email will be sent.

### 1.3. Technology Stack

No new technologies are required. The implementation will use the existing stack:
*   **Backend:** Python, FastAPI
*   **Frontend:** Next.js, React

---

## Phase 2: Tactical Sprint Plan

The work will be completed in a single, focused sprint.

### Sprint 1: Implement Email Notifications

*   **Sprint ID & Name:** S1: Access Request Email Notifications
*   **Project Context:** This sprint focuses on enhancing the administrator's access request management system by automating email notifications for approvals and denials.
*   **Goal:** To fully implement and test the automated email notification feature.
*   **Tasks:**

    1.  **Backend: Create Email Templates:**
        *   Create two email templates:
            1.  `access-approved.html`: An email template that includes a placeholder for the temporary passcode.
            2.  `access-denied.html`: A template with a polite message informing the user their request was denied.

    2.  **Backend: Update Access Request Service:**
        *   Modify the `approve_access_request_and_create_user` function in the `access_request_service.py`.
        *   After successfully creating the user and generating the temporary password, call the existing email service to send the `access-approved.html` email to the requestor, populating it with the new passcode.
        *   Modify the `update_access_request` function (or the relevant denial logic).
        *   When a request's status is changed to "denied", call the email service to send the `access-denied.html` email.
        *   **User Test:** Ask the user to test the approval and denial endpoints using an API client (like Insomnia/Postman) and verify that the correct emails are sent and received.

    3.  **Frontend: Update UI:**
        *   In the `frontend/app/(main)/access-requests/page.tsx` file, add a small, non-intrusive UI element to inform the admin that an email notification will be sent upon approval or denial. A simple line of text below the action buttons is sufficient (e.g., "The user will be notified by email.").
        *   Modify the success toast notifications that appear after approving or denying a request to confirm that an email has been sent (e.g., "Access request approved and user notified by email.").
        *   **User Test:** Ask the user to review the updated UI on the access requests page and confirm the new text and toast messages appear as expected.

    4.  **Final E2E Test & Commit:**
        *   Perform a final end-to-end test by approving and denying a request from the UI.
        *   Verify the UI responds correctly.
        *   Verify the correct emails are received.
        *   After the user confirms all functionality is working as expected, commit all changes with a descriptive message (e.g., "feat: implement email notifications for access requests").

*   **Verification Criteria:** An administrator can approve or deny an access request from the UI, and the system automatically sends the correct email notification to the requestor. The UI provides feedback that the notification has been sent.