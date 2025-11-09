# Gemini Agent Guidelines for 808Found Frontend

This document provides specific guidelines and context for the Gemini AI agent when working with the 808Found frontend codebase. Its purpose is to enable the agent to interact efficiently and effectively with the project, adhering to established conventions and best practices.

## Project Overview for Gemini

*   **Project Type:** Next.js Application (version 16)
*   **Language:** TypeScript
*   **UI Framework:** React (version 19)
*   **Styling:** Tailwind CSS (version 4)
*   **Component Library:** Shadcn UI (built on Radix UI)
*   **Package Manager:** pnpm
*   **Key Features:** Financial analysis, backtesting, data visualization, interactive dashboards, 3D graphics.

## Core Mandates for Gemini

1.  **Adhere to Conventions:** Always prioritize existing code conventions, styling, and architectural patterns. Analyze surrounding code before making changes.
2.  **Verify Library Usage:** Never assume a library is available. Check `package.json`, `tsconfig.json`, and existing imports before using new libraries or frameworks.
3.  **Idiomatic Changes:** Ensure all modifications integrate naturally and idiomatically with the local context.
4.  **Testing:** When adding features or fixing bugs, always consider adding or updating relevant tests.
5.  **Verification:** After any code changes, run linting and type-checking commands to ensure code quality.

## Important Commands and Scripts

The following commands are available and should be used for development, building, and quality checks:

*   **Install Dependencies:**
    ```bash
    pnpm install
    ```
*   **Run Development Server:**
    ```bash
    pnpm dev
    ```
    (Accessible at `http://localhost:3000`)
*   **Build for Production:**
    ```bash
    pnpm build
    ```
*   **Start Production Server:**
    ```bash
    pnpm start
    ```
*   **Run Linter:**
    ```bash
    pnpm lint
    ```
    *Note: This project uses ESLint. Always ensure linting passes after making changes.*

## Testing Strategy

Currently, there is no explicit `test` script defined in `package.json`. If testing is required:

*   **Inquire:** Ask the user about the preferred testing framework (e.g., Jest, React Testing Library, Playwright, Cypress) and how to set it up or run existing tests.
*   **Component-level Testing:** For new components or significant changes, consider suggesting the creation of unit/integration tests.

## Codebase Specifics

*   **UI Components:** Most UI components reside in `src/components/ui/` (Shadcn UI) and `src/ui-components/` (custom/external UI libraries). When creating new UI elements, follow the patterns established in these directories.
*   **Pages:** Main application pages are located in `src/app/` and `src/components/pages/`.
*   **Utilities:** Common utility functions are in `src/lib/utils.ts`.
*   **Hooks:** Custom React hooks are in `src/hooks/`.
*   **3D Graphics:** Components utilizing `react-three/fiber` and `three.js` are found in `src/components/webgl/`. Be mindful of performance when working with these.

## When to Consult the User

*   **Major Architectural Changes:** Any significant changes to the project's architecture or core technologies.
*   **New Dependencies:** Before introducing new libraries or frameworks not already present.
*   **Ambiguous Requirements:** If the task description is unclear or has multiple possible interpretations.
*   **Testing Framework Setup:** If tests need to be added and no framework is currently configured.

By following these guidelines, Gemini can effectively assist in the development and maintenance of the 808Found frontend.