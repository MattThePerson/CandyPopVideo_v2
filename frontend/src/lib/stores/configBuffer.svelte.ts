function createConfigBuffer() {
    let content = $state<string>(localStorage.getItem('configBuffer') ?? '');
    let savedAt  = $state<string>(localStorage.getItem('configBufferSavedAt') ?? '');

    const isDirty = $derived(content !== '');

    return {
        get content()  { return content; },
        set content(v: string) {
            content = v;
            savedAt = new Date().toISOString();
            localStorage.setItem('configBuffer', v);
            localStorage.setItem('configBufferSavedAt', savedAt);
        },
        get savedAt()  { return savedAt; },
        get isDirty()  { return isDirty; },
        clear() {
            content = '';
            savedAt = '';
            localStorage.removeItem('configBuffer');
            localStorage.removeItem('configBufferSavedAt');
        },
    };
}

export const configBuffer = createConfigBuffer();
