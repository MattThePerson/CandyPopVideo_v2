# frontend/CLAUDE.md

Svelte 5 + TypeScript + Tailwind v4 frontend. These rules apply to all files under `frontend/`.

## Formatting

### Svelte file structure

Every Svelte file with both a `<script>` block and an HTML template must include a visual separator between them, and another before `<style>` if a style block exists:

```html
<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->
```

```html
<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->
```

Files with no `<script>` block omit the HTML separator. Files with no `<style>` block omit the CSS separator. Stub pages with neither skip both.

### Page.svelte path comment

Every `Page.svelte` file must have a comment on the very first line with its path relative to `src/`:

```html
<!-- pages/video/Page.svelte -->
```

### Props comment

If a component uses `$props()`, put `/* Props */` on the line immediately above it.

### Function comments

Add a short comment above any function whose purpose isn't immediately obvious from its name. Skip trivial one-liners and self-evident CRUD calls (e.g. `addLike()`). Do include a comment when:
- the function has a non-obvious implementation detail
- it works around a third-party quirk
- it uses optimistic UI (note "Optimistic — reverts on error")
