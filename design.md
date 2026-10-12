# UI/UX Design System & Specification
## The Lenny Growth Assistant

**Status:** Approved  
**Author:** Senior Product Designer & Full-Stack AI Engineer  
**Version:** 1.0.0  

---

## 1. Visual Design Philosophy

The Lenny Growth Assistant interface is designed as a **premium, focused AI SaaS workspace**. The design language embodies clarity, elegance, and density suitable for executives and product builders.

* **Palette Atmosphere:** 
  * Primary workspace: Crisp, clean, light background (`#F8FAFC` to `#FFFFFF`) with subtle slate borders (`#E2E8F0`).
  * Navigation sidebar: Deep Midnight Navy (`#0B1120`) providing grounding and contrast.
  * Accents: Restrained violet (`#7C3AED` / `#8B5CF6`) and royal blue (`#2563EB`) representing intelligence and action.
* **Typography:**
  * Primary Interface: `Inter`, sans-serif (weights: 400, 500, 600, 700).
  * Monospace / Code / Artifacts: `JetBrains Mono` or `Fira Code`.
* **Micro-Interactions:**
  * Subtle hover elevations (`shadow-sm` transitioning to `shadow-md`).
  * Smooth transitions on panel expand/collapse (`transition-all duration-200 ease-in-out`).
  * No excessive, distracting animations or dizzying gradient washes.

---

## 2. Color Palette Token System

| Token Name | Hex Code | Purpose |
| :--- | :--- | :--- |
| `navy-950` | `#070C18` | Deep sidebar background |
| `navy-900` | `#0B1120` | Secondary sidebar surface / active conversation |
| `navy-800` | `#1E293B` | Sidebar border / divider |
| `slate-50`  | `#F8FAFC` | Main chat workspace background |
| `slate-100` | `#F1F5F9` | Card surfaces / assistant bubble background |
| `slate-200` | `#E2E8F0` | Input borders, subtle dividers |
| `slate-600` | `#475569` | Secondary helper text |
| `slate-900` | `#0F172A` | Primary typography color |
| `violet-600`| `#7C3AED` | Primary brand accent / button fill |
| `violet-700`| `#6D28D9` | Button active / hover state |
| `blue-600`  | `#2563EB` | Active citation links / provider tags |
| `emerald-600`| `#059669`| Success badges / system online indicator |
| `amber-500` | `#D97706` | Warning status (e.g., local model offline) |

---

## 3. Desktop Three-Panel Layout Architecture

```
+------------------+----------------------------------+-----------------------------+
| SIDEBAR (260px)  | MAIN CHAT WORKSPACE (Flex-1)     | ARTIFACT VIEWER (480-600px) |
| [Logo] Lenny GA  | Top Bar: Title | Model Picker    | Tabs: [Preview] [Code]      |
| [+ New Chat]     |                                  | Actions: [Copy] [Download]  |
|                  | Welcome Screen / Messages Feed   |                             |
| Search chats...  |                                  | --------------------------- |
|                  | [User Bubble]                    |                             |
| RECENT SESSIONS  |                                  | Live Rendered Artifact     |
| * Elena Verna B2B| [Assistant Bubble]               | (Sandboxed Iframe           |
| * PMF 3-Month... |   - Grounded Answer Markdown     |  or Clean Markdown view)    |
| * Retention Loop |   - Source Citation Badges       |                             |
|                  |                                  |                             |
| [Settings/Status]| Bottom Bar: Multi-line Input     |                             |
+------------------+----------------------------------+-----------------------------+
```

### A. Left Sidebar
* **Top Header:** Application icon (sparkles / growth chart) and title **"Lenny Growth Assistant"**.
* **Primary Action:** Prominent `+ New Chat` button with keyboard hint (`Ctrl+N` / `Cmd+N`).
* **Search Filter:** Instant client-side search box filtering conversation titles.
* **Conversation List:**
  * Chronologically grouped or listed by recent activity.
  * Active conversation highlighted with subtle violet border and navy tint.
  * Inline action menu (hover-activated): Rename conversation, Delete conversation with confirmation dialog.
* **Bottom Status Bar:** Live backend connectivity status indicator (Online / Offline / Model: Ollama).

### B. Main Chat Workspace
* **Top Header Bar:**
  * Current conversation title with inline click-to-edit.
  * Model/Provider Dropdown Selector (`Ollama (Local)` / `OpenAI` / `Anthropic`).
  * Artifact toggle button (if artifacts have been generated in the thread).
* **Welcome Screen (Empty State):**
  * Displays friendly avatar and title: *"What growth challenges are you solving today?"*
  * 4 quick-start prompt cards:
    1. **B2B Growth Playbook:** *"How does Elena Verna reinvent growth loops for AI products?"*
    2. **Product-Market Fit:** *"What are the signs of true PMF according to Marc Andreessen and Peter Sellis?"*
    3. **Ship 30 Essay:** *"Write a Ship 30 for 30 essay on why retention eats acquisition."*
    4. **Webpage Generator:** *"Generate an interactive PM feature prioritization calculator in HTML/CSS."*
* **Chat Stream:**
  * User bubble: Clean slate pill aligned to right or distinguished with subtle border.
  * Assistant bubble: Clean white background with subtle border, rich markdown formatting (tables, bullet points, headers).
  * Citation accordion: Expandable cards below answer showing:
    - Guest name and episode title
    - Exact dialogue excerpt
    - Outbound link to full Lenny's Newsletter post
  * Message actions: One-click "Copy response", "Generate Essay from this", and "Open Artifact".
* **Chat Input Area:**
  * Auto-resizing multi-line textarea (`Shift+Enter` for new line, `Enter` to send).
  * Send button with loading spinner during inference.

### C. Artifact Viewer Panel
* **Collapsible / Resizable:** Can be toggled open or closed without interrupting the chat thread.
* **Header Controls:**
  * Artifact title & type pill (`Markdown Document` or `HTML/CSS Webpage`).
  * Tab toggle: **Preview** vs. **Code**.
  * Action buttons: **Copy Source Code** and **Download File (.md / .html)**.
  * Close / minimize button.
* **Preview Tab:**
  * If HTML: Securely rendered inside an isolated `iframe` with `sandbox="allow-scripts"`.
  * If Markdown: Rendered with beautiful GitHub-style markdown typography and styling.
* **Code Tab:**
  * Monospace code block with syntax highlighting and line numbers.

---

## 4. Responsive Breakpoints

* **Desktop ($\ge 1200\text{px}$):** Full 3-panel layout visible simultaneously.
* **Tablet ($768\text{px} - 1199\text{px}$):** Sidebar collapses into a slide-over drawer; Artifact viewer opens as an overlay side panel or split-screen.
* **Mobile ($< 768\text{px}$):** Single panel at a time; Tabbed switching between Chat and Artifact Viewer; Drawer sidebar.

---

## 5. Accessibility (a11y) & Focus Management

* **Color Contrast:** All text meets or exceeds WCAG AA standards ($> 4.5:1$ contrast ratio).
* **Keyboard Navigation:**
  * `Tab` key moves logically through sidebar items, model selector, message links, and input area.
  * Visible ring focus indicators (`focus:ring-2 focus:ring-violet-500`).
* **ARIA Attributes:** Modals use `aria-modal="true"`, buttons include meaningful `aria-label` tags, and loading states include `aria-busy="true"`.
