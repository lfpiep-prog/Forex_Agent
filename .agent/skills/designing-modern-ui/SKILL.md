---
name: designing-modern-ui
description: Designs modern, responsive UIs using Tailwind CSS and React best practices. Use when the user asks for new UI components, styling changes, or frontend features.
---

# Modern UI Design

## When to use this skill
- User requests a new web page or component.
- User wants to "modernize" or "style" an existing page.
- User asks for Tailwind CSS or React implementations.

## Workflow
- [ ] **Analyze Requirements**: specific elements, color scheme, responsiveness.
- [ ] **Check Existing System**: Look for `tailwind.config.js` or `index.css` to reuse tokens.
- [ ] **Plan Component**: Define the structure (HTML/JSX) and styling strategy.
- [ ] **Implement**: Write the code using functional components and utility classes.
- [ ] **Verify**: Check for mobile responsiveness and accessibility constraints.

## Instructions
1.  **Mobile First**: Always write styles that work on mobile default, then use `md:` or `lg:` for larger screens.
2.  **Use Tokens**: Do not hardcode hex values (e.g., `#3b82f6`). Use Tailwind classes (e.g., `bg-blue-500`).
3.  **Composition**: Break complex UIs into smaller components.
4.  **Accessibility**:
    -   All images must have `alt` text.
    -   Buttons must have clear labels or `aria-label`.
5.  **Aesthetics**:
    -   Use generous whitespace (`p-4`, `gap-4`).
    -   Use subtle shadows (`shadow-sm`, `shadow-lg`) for depth.
    -   Use rounded corners (`rounded-lg`) for a modern feel.

## Resources
- [Tailwind Cheatsheet](https://tailwindcss.com/docs) (Mental Model: Utility-first)
