<script lang="ts">
    /* Props */
    const { message, confirmLabel = 'Confirm', onConfirm, onCancel }: {
        message:      string;
        confirmLabel?: string;
        onConfirm:    () => void;
        onCancel:     () => void;
    } = $props();

    $effect(() => {
        function onKey(e: KeyboardEvent) {
            if (e.key === 'Escape') onCancel();
        }
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="backdrop" onclick={onCancel} role="presentation">
    <div class="modal" role="dialog" tabindex="-1" onclick={(e) => e.stopPropagation()}>
        <p class="message">{message}</p>
        <div class="actions">
            <button class="btn-cancel" onclick={onCancel}>Cancel</button>
            <button class="btn-primary" onclick={onConfirm}>{confirmLabel}</button>
        </div>
    </div>
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.75);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .modal {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 1.5rem;
        width: min(420px, 90vw);
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
    }

    .message {
        color: #ccc;
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
    }

    .actions {
        display: flex;
        gap: 0.75rem;
        justify-content: flex-end;
    }

    .btn-cancel {
        background: #2a2a2a;
        border: 1px solid #444;
        color: #999;
        font-size: 0.83rem;
        border-radius: 5px;
        padding: 0.45rem 1rem;
        cursor: pointer;
    }

    .btn-primary {
        background: #f97316;
        border: none;
        color: #000;
        font-weight: 600;
        font-size: 0.83rem;
        border-radius: 5px;
        padding: 0.45rem 1rem;
        cursor: pointer;
    }

    .btn-cancel:hover { background: #333; color: #ddd; }
    .btn-primary:hover { background: #ea6c0b; }
</style>
