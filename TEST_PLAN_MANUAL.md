# Manual UI & End-to-End Test Plan
## The Lenny Growth Assistant

This document provides a systematic test script for evaluators, QA engineers, and developers to verify that all functional requirements, security boundaries, and user interactions work smoothly.

---

### Test Case 1: Application Health & Initial Load
* **Objective:** Verify frontend loads without errors and backend API is reachable.
* **Steps:**
  1. Navigate to `http://localhost:5173` (or `http://localhost:3000` via Docker).
  2. Observe the Left Sidebar, Chat Workspace, and status card at bottom left.
* **Expected Result:**
  * Sidebar displays application title *"Lenny Assistant"* with deep navy theme (`#0B1120`).
  * Bottom left card shows green pulse indicator: *"Engine Online"* and displays *"2483 transcript chunks indexed"*.
  * Main workspace displays the welcome screen with 4 example prompt cards.

---

### Test Case 2: Grounded Q&A with Real Citations
* **Objective:** Ensure answers are grounded in Lenny's Podcast transcripts with accurate source metadata.
* **Steps:**
  1. Click the first prompt card or type: *"How does Elena Verna reinvent growth loops for AI-native companies?"*
  2. Hit `Enter`.
* **Expected Result:**
  * User message bubble appears in feed.
  * Loading state displays *"Searching Transcripts & Synthesizing..."*.
  * Assistant returns a grounded answer attributing insights to Elena Verna and Lovable's growth model.
  * Below the response, a *"Verified Podcast Sources"* accordion renders source citation cards.
  * Click on a citation card to expand and view the exact spoken transcript excerpt and date.
  * Click the external link icon to verify it points to the genuine Lenny's Newsletter post.

---

### Test Case 3: Preserving Conversation Context Across Follow-ups
* **Objective:** Ensure follow-up questions retain the active thread context.
* **Steps:**
  1. In the same conversation, type: *"What does she recommend regarding building in public vs optimization?"*
  2. Hit `Enter`.
* **Expected Result:**
  * Assistant understands "she" refers to Elena Verna from the previous turn.
  * Response synthesizes her specific advice (spending 95% innovating on high-conviction bets vs 5% on optimization) without losing the context of Lovable or B2B growth.

---

### Test Case 4: Multi-Session Isolation
* **Objective:** Ensure new conversations start with clean, isolated context.
* **Steps:**
  1. Click the `+ New Conversation` button in the sidebar.
  2. Confirm the chat workspace resets to the Welcome Screen.
  3. Type: *"Who were we just talking about in the previous chat?"*
  4. Hit `Enter`.
* **Expected Result:**
  * The assistant does NOT leak knowledge of Elena Verna from the previous chat.
  * It correctly states that this is a fresh conversation with no prior turns.
  * The previous conversation remains saved in the sidebar and can be switched back to at any time.

---

### Test Case 5: Model Provider Switching
* **Objective:** Verify switching between local Ollama and cloud LLMs.
* **Steps:**
  1. Click the model dropdown in the top header (currently showing e.g., *"Ollama (llama3.2)"*).
  2. Select *"OpenAI GPT-4o Mini"* or *"Anthropic Claude 3.5 Sonnet"*.
  3. Notice the provider badge update in the UI.
  4. Send a test prompt.
* **Expected Result:**
  * The selected provider is stored in application state and sent with the chat request.
  * The assistant response badge indicates the active model used for generation.

---

### Test Case 6: Ship 30 for 30 Essay Generation
* **Objective:** Verify the dedicated Ship 30 essay skill engine.
* **Steps:**
  1. Click the *"Ship 30 Essay"* quick skill pill above the input box or type:
     *"Write a Ship 30 for 30 essay on why retention eats acquisition."*
  2. Hit `Enter`.
* **Expected Result:**
  * Assistant notifies you that the essay has been generated.
  * The **Artifact Viewer** panel automatically opens on the right.
  * The essay exhibits the full Ship 30 format:
    * Clear Headline
    * 1-3-1 Hook & Lead
    * Descriptive subheadings (`##`)
    * Selective bolding on key phrases for speed-readers
    * Actionable bullet points
    * Golden Takeaway summary
  * Word count approaches ~1,250 words.

---

### Test Case 7: Interactive HTML/CSS Webpage Generation & Sandboxed Iframe
* **Objective:** Verify generation of interactive web components and secure sandbox boundaries.
* **Steps:**
  1. Click the *"HTML Webpage"* quick skill pill or type:
     *"Generate an interactive HTML/CSS webpage component for calculating viral factor K."*
  2. Hit `Enter`.
* **Expected Result:**
  * Assistant generates the component and mounts it into the **Artifact Viewer**.
  * Under the **Preview** tab, the interactive calculator is fully functional: you can type inputs and click the calculation button inside the iframe.
  * Inspect the DOM with browser DevTools (`F12`) to confirm the `iframe` has `sandbox="allow-scripts"` and does NOT have `allow-same-origin`.
  * Open the browser console inside the iframe to confirm it cannot access `window.parent.document` or parent cookies.

---

### Test Case 8: Code Inspection, Copy, and File Export
* **Objective:** Verify artifact viewer code tab and download capabilities.
* **Steps:**
  1. In the Artifact Viewer, switch to the **Code** tab.
  2. Confirm the syntax is rendered with line numbers in clean monospace font.
  3. Click **Copy**: confirm button changes to *"Copied"* with green checkmark.
  4. Click **Export**: confirm browser downloads a clean `.html` or `.md` file to your Downloads folder.

---

### Test Case 9: Conversation Management (Rename & Delete)
* **Objective:** Verify conversation CRUD and modal interactions.
* **Steps:**
  1. Hover over a conversation in the sidebar and click the **Edit** (pencil) icon.
  2. Rename it to *"My Custom Growth Strategy"*.
  3. Click **Save Title**; confirm title updates in sidebar and header.
  4. Hover over the conversation and click the **Delete** (trash) icon.
  5. In the confirmation modal, click **Delete Conversation**.
* **Expected Result:**
  * Conversation is removed from the sidebar and deleted from database storage.
  * The workspace safely transitions to a fresh chat screen.
